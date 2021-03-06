import cPickle
import os.path as osp

from smqtk.representation.code_index import CodeIndex
from smqtk.utils import SimpleTimer


__author__ = "paul.tunison@kitware.com"


class MemoryCodeIndex (CodeIndex):
    """
    Local RAM memory based index with an optional file cache
    """

    @classmethod
    def is_usable(cls):
        """
        No outside dependencies.
        :rtype: bool
        """
        return True

    def __init__(self, file_cache=None):
        """
        Initialize a new in-memory code index, or reload one from a cache.

        :param file_cache: Optional path to a file path, loading an existing
            index if the file already exists. Either way, providing a path to
            this enabled file caching when descriptors are added to this index.
            This cache file is a pickle serialization.
        :type file_cache: None | str

        """
        super(MemoryCodeIndex, self).__init__()

        self._num_descr = 0
        self._file_cache = file_cache

        # Mapping of code to a dictionary mapping descrUUID->Descriptor
        #: :type: dict[collections.Hashable, dict[collections.Hashable, smqtk.representation.DescriptorElement]]
        self._table = {}
        if file_cache and osp.isfile(file_cache):
            with open(file_cache) as f:
                self._log.debug("Loading cached code index table from file: %s",
                                file_cache)
                #: :type: dict[collections.Hashable, dict[collections.Hashable, smqtk.representation.DescriptorElement]]
                self._table = cPickle.load(f)
                self._log.debug("Counting indexed descriptors")
                # Find the number of descriptors in the table
                self._num_descr = sum(len(d) for d in self._table.itervalues())
                self._log.debug("Done loading cached table")

    def cache_table(self):
        """
        If a file cache has been specified, cache the current memory table state
        to the cache. Otherwise, this function does nothing.
        """
        if self._file_cache:
            with SimpleTimer("Caching memory table", self._log.debug):
                with open(self._file_cache, 'wb') as f:
                    cPickle.dump(self._table, f)

    def get_config(self):
        return {
            "file_cache": self._file_cache
        }

    def count(self):
        """
        :return: Number of descriptor elements stored in this index. This is not
            necessarily the number of codes stored in the index.
        :rtype: int
        """
        return self._num_descr

    def clear(self):
        """
        Clear this code index's table entries.
        """
        self._table = {}
        self.cache_table()

    def codes(self):
        """
        :return: Set of code integers currently used in this code index.
        :rtype: set[int]
        """
        return set(self._table)

    def iter_codes(self):
        """
        Iterate over code contained in this index in an arbitrary order.

        :return: Generator that yields integer code keys
        :rtype: collections.Iterator[int|long]

        """
        for k in self._table:
            yield k

    def add_descriptor(self, code, descriptor, no_cache=False):
        """
        Add a descriptor to this index given a matching small-code

        :param code: bit-hash of the given descriptor in integer form
        :type code: int

        :param descriptor: Descriptor to index
        :type descriptor: smqtk.representation.DescriptorElement

        :param no_cache: Do not cache the internal table if a file cache was
            provided. This option should not be modified from its default by
            normal use. Used internally.
        :type no_cache: bool

        """
        code_map = self._table.setdefault(code, {})
        if descriptor.uuid() not in code_map:
            self._num_descr += 1
        code_map[descriptor.uuid()] = descriptor
        if not no_cache:
            self.cache_table()

    def add_many_descriptors(self, code_descriptor_pairs):
        """
        Add multiple code/descriptor pairs.

        :param code_descriptor_pairs: Iterable of integer code and paired
            descriptor tuples to add to this index.
        :type code_descriptor_pairs:
            collections.Iterable[(int, smqtk.representation.DescriptorElement)]

        """
        for c, d in code_descriptor_pairs:
            self.add_descriptor(c, d, True)
        self.cache_table()

    def get_descriptors(self, code_or_codes):
        """
        Get iterable of descriptors associated to this code or iterable of
        codes. This may return an empty iterable.

        :param code_or_codes: An integer or iterable of integer bit-codes.
        :type code_or_codes: collections.Iterable[int] | int

        :return: Iterable of descriptors
        :rtype: collections.Iterable[smqtk.representation.DescriptorElement]

        """
        if hasattr(code_or_codes, '__iter__'):
            # noinspection PyTypeChecker
            # -> I literally just checked for __iter__
            for c in code_or_codes:
                for v in self._table.get(c, {}).values():
                    yield v
        else:  # assuming int
            for v in self._table.get(code_or_codes, {}).itervalues():
                yield v


CODE_INDEX_CLASS = MemoryCodeIndex
