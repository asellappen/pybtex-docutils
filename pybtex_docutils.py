"""
.. autoclass:: Backend
   :show-inheritance:
   :members: citation, citation_reference
"""

import docutils.nodes
import itertools

from pybtex.backends import BaseBackend
import pybtex.richtext


class Backend(BaseBackend):
    name = 'docutils'

    symbols = {
        'ndash': [docutils.nodes.Text(u'\u2013', u'\u2013')],
        'newblock': [docutils.nodes.Text(u' ', u' ')],
        'nbsp': [docutils.nodes.Text(u'\u00a0', u'\u00a0')],
    }
    tags = {
        'emph': docutils.nodes.emphasis,
    }
    RenderType = list

    # for compatibility only
    def format_text(self, text):
        return self.format_str(text)

    def format_str(self, str_):
        assert isinstance(str_, basestring)
        return [docutils.nodes.Text(str_, str_)]

    def format_tag(self, tag_name, text):
        assert isinstance(tag_name, basestring)
        assert isinstance(text, self.RenderType)
        tag = self.tags[tag_name]
        node = tag('', '', *text)
        return [node]

    def format_href(self, url, text):
        assert isinstance(url, basestring)
        assert isinstance(text, self.RenderType)
        node = docutils.nodes.reference('', '', *text, refuri=url)
        return [node]

    def write_entry(self, key, label, text):
        raise NotImplementedError("use Backend.citation() instead")

    def render_sequence(self, rendered_list):
        """Return backend-dependent representation of sequence *text*
        of rendered Text objects.
        """
        return list(itertools.chain(*rendered_list))

    def paragraph(self, entry):
        """Return a docutils.nodes.paragraph
        containing the rendered text for *entry* (without label).
        """
        return docutils.nodes.paragraph('', '', *entry.text.render(self))

    def citation(self, entry, document, use_key_as_label=True):
        """Return citation node, with key as name, label as first
        child, and rendered text as second child. The citation is
        expected to be inserted into *document* prior to any docutils
        transforms.
        """
        # see docutils.parsers.rst.states.Body.citation()
        if use_key_as_label:
            label = entry.key
        else:
            label = entry.label
        name = docutils.nodes.fully_normalize_name(entry.key)
        text = entry.text.render(self)
        citation = docutils.nodes.citation()
        citation['names'].append(name)
        citation += docutils.nodes.label('', label)
        citation += self.paragraph(entry)
        document.note_citation(citation)
        document.note_explicit_target(citation, citation)
        return citation

    def citation_reference(self, entry, document, use_key_as_label=True):
        """Return citation_reference node to the given citation. The
        citation_reference is expected to be inserted into *document*
        prior to any docutils transforms.
        """
        # see docutils.parsers.rst.states.Body.footnote_reference()
        if use_key_as_label:
            label = entry.key
        else:
            label = entry.label
        refname = docutils.nodes.fully_normalize_name(entry.key)
        refnode = docutils.nodes.citation_reference(
            '[%s]_' % label, refname=refname)
        refnode += docutils.nodes.Text(label)
        document.note_citation_ref(refnode)
        return refnode
