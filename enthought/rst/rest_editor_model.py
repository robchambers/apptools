#------------------------------------------------------------------------------
#
#  Copyright (c) 2009, Enthought, Inc.
#  All rights reserved.
# 
#  This software is provided without warranty under the terms of the BSD
#  license included in enthought/LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Thanks for using Enthought open source!
#  
#  Author: Evan Patterson
#  Date:   06/18/2009
#
#------------------------------------------------------------------------------

# Standard library imports
import codecs
import os.path
from multiprocessing import Pool
from shutil import rmtree
from tempfile import mkdtemp

# System library imports
import docutils.io, docutils.nodes
from docutils.core import Publisher

# ETS imports
from enthought.traits.api import HasTraits, Int, Str, List, Bool, Any, \
    Property, on_trait_change
from enthought.traits.ui.extras.saving import CanSaveMixin


class NullIO: 
    """ A dummy stream-like object which swallows all its messages.
    """
    def write(self, message):
        pass


def docutils_rest_to_html(rest):
    """ Uses docutils to convert a ReST string to HTML. Returns a tuple
        containg the HTML string and the list of warning nodes that were
        removed from the HTML.
    """
    pub = Publisher(source_class=docutils.io.StringInput,
                    destination_class=docutils.io.StringOutput)
    pub.set_reader('standalone', None, 'restructuredtext')
    pub.set_writer('html')
    pub.get_settings() # Get the default settings
    pub.settings.halt_level = 6 # Don't halt on errors
    pub.settings.warning_stream = NullIO()

    pub.set_source(rest)
    pub.set_destination()
    pub.document = pub.reader.read(pub.source, pub.parser, pub.settings)
    pub.apply_transforms()

    # Walk the node structure of a docutils document and remove 'problematic'
    # and 'system_message' nodes. Save the system_message nodes.
    warning_nodes = []
    for node in pub.document.traverse(docutils.nodes.problematic):
        node.parent.replace(node, node.children[0])
    for node in pub.document.traverse(docutils.nodes.system_message):
        warning_nodes.append(node)
        node.parent.remove(node)

    return pub.writer.write(pub.document, pub.destination), warning_nodes


def sphinx_rest_to_html(rest):
    """ Uses sphinx ro convert a ReST string to HTML. Requires the use of 
        temporary files. Returns the same things as docutils_rest_to_html.
    """

    # Hijack the warning filter method in Sphinx so that we can save the nodes
    # that were removed.
    warning_nodes = []
    def my_filter_messages(self, doctree):
        for node in doctree.traverse(docutils.nodes.system_message):
            warning_nodes.append(node)
            node.parent.remove(node)
    import sphinx.environment
    sphinx.environment.BuildEnvironment.filter_messages = my_filter_messages

    from sphinx.application import Sphinx

    temp_dir = mkdtemp(prefix='rest-editor-')
    try:
        filename = 'sphinx_preview'
        base_path = os.path.join(temp_dir, filename)
        fh = codecs.open(base_path+'.rst', 'w', 'utf-8')
        fh.write(rest)
        fh.close()

        overrides = { 'html_add_permalinks' : False,
                      'html_copy_source' : False, 
                      'html_title' : 'Sphinx preview',
                      'html_use_index' : False, 
                      'html_use_modindex' : False,
                      'html_use_smartypants' : True, 
                      'master_doc' : filename }
        app = Sphinx(srcdir=temp_dir, confdir=None, outdir=temp_dir, 
                     doctreedir=temp_dir, buildername='html', 
                     confoverrides=overrides, status=None, warning=NullIO())
        app.build(all_files=True, filenames=None)

        fh = codecs.open(base_path+'.html', 'r', 'utf-8')
        html = fh.read()
        fh.close()
    finally:
        rmtree(temp_dir)

    return html, warning_nodes


class DocUtilsWarning(HasTraits):

    level = Int
    line = Int
    description = Str


class ReSTHTMLPair(CanSaveMixin):
    rest = Str
    html = Str
    warnings = List(DocUtilsWarning)

    use_sphinx = Bool(False)

    save_html = Bool(False)
    # The 'filepath' attribute of CanSaveMixin is for the ReST file
    html_filepath = Property(Str, depends_on='filepath')

    # Private traits
    _pool = Any
    _processing = Bool(False)
    _queued = Bool(False)

    #-----------------------------------------------------------------
    #  ReSTHTMLPair interface
    #-----------------------------------------------------------------

    def __init__(self, **kw):
        self._pool = Pool(processes=1)
        super(ReSTHTMLPair, self).__init__(**kw)
        self._queue_html()

    def _rest_changed(self):
        self.dirty = True

    @on_trait_change('rest, use_sphinx')
    def _queue_html(self):
        if self._processing:
            self._queued = True
        else:
            self._processing = True
            self._gen_html()
            
    def _gen_html(self):
        func = sphinx_rest_to_html if self.use_sphinx else docutils_rest_to_html
        self._pool.apply_async(func, [self.rest], callback=self._set_html)

    def _set_html(self, result):
        if self._queued:
            self._gen_html()
            self._queued = False
        else:
            self.html, warning_nodes = result
            warnings = []
            for node in warning_nodes:
                description = node.children[0].children[0].data
                warnings.append(DocUtilsWarning(level=node.attributes['level'],
                                                line=node.attributes['line'],
                                                description=description))
            self.warnings = warnings
            self._processing = False

    def _get_html_filepath(self):
        filepath = self.filepath
        index = filepath.rfind('.')
        if index != -1:
            filepath = filepath[:index]
        return filepath + '.html'

    #-----------------------------------------------------------------
    #  CanSaveMixin interface
    #-----------------------------------------------------------------

    def validate(self):
        """ Prompt the user if there are warnings/errors with reST file.
        """
        if len(self.warnings):
            return (False, "The reStructured Text is improperly composed." \
                           "Are you sure you want to save it?")
        else:
            return (True, '')

    def save(self):
        """ Save both the reST and HTML file.
        """
        self.dirty = False

        fh = codecs.open(self.filepath, 'w', 'utf-8')
        fh.write(self.rest)
        fh.close()

        if self.save_html:
            fh = codecs.open(self.html_filepath, 'w', 'utf-8')
            fh.write(self.html)
            fh.close()