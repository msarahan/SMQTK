# High-level Algorithm Interfaces
Here we list and briefly describe the high level algorithm interfaces which SMQTK provides.
There is at least one implementation available for each interface.
Some implementations will require additional dependencies that cannot be packaged with SMQTK.


## [``DescriptorGenerator``](/python/smqtk/algorithms/descriptor_generator/__init__.py)
This interface represents algorithms that generate whole-content descriptor vectors for a single given input ``DataElement`` instance.
The input ``DataElement`` must be of a content type that the ``DescriptorGenerator`` supports, referenced against the ``DescriptorGenerator.valid_content_types`` method.

The ``compute_descriptor`` method also requires a ``DescriptorElementFactory`` instance to tell the algorithm how to generate the ``DescriptorElement`` it should return.
The returned ``DescriptorElement`` instance will have a type equal to the name of the ``DescriptorGenerator`` class that generated it, and a UUID that is the same as the input ``DataElement`` instance.

If a ``DescriptorElement`` implementation that supports persistant storage is generated, and there is already a descriptor associated with the given type name and UUID values, the descriptor is returned without re-computation.

If the ``overwrite`` parameter is ``True``, the ``DescriptorGenerator`` instance will re-compute a descriptor for the input ``DataElement``, setting it to the generated ``DescriptorElement``. This will overwrite descriptor data in persistant storage if the ``DescriptorElement`` type used supports it.

This interface supports a high-level, implementation agnostic asynchronous descriptor computation method.
This is given an iterable of ``DataElement`` instances, a single ``DescriptorElementFactory`` that is used to produce all descriptor


## [``NearestNeighborsIndex``](/python/smqtk/algorithms/nn_index/__init__.py)
This interface defines a method to build an index from a set of ``DescriptorElement`` instances (``NearestNeighborsIndex.build_index``) and a nearest-neighbors query function for getting a number of near neighbors to e query ``DescriptorElement`` (``NearestNeighborsIndex.nn``).

Building an index requires that some non-zero number of ``DescriptorElements`` be passed into the ``build_index`` method. Subsequent calls to this method should rebuild the index model, not add to it.
If an implementation supports persistant storage of the index, it should overwrite the configured index.

The ``nn`` method uses a single ``DescriptorElement`` to query the current index for a specified number of nearest neighbors.
Thus, the ``NearestNeighborsIndex`` instance must have a non-empty index loaded for this method to function.
If the provided query ``DescriptorElement`` does not have a set vector, this method will also fail with an exception.

This interface additionally requires that implementations define a ``count`` method, which returns the number of distinct ``DescriptorElement``instances are in the index.


## [``RelevancyIndex``](/python/smqtk/algorithms/relevancy_index/__init__.py)
This interface defines two methods: ``build_index`` and ``rank``.
The ``build_index`` method is, like a ``NearestNeighborsIndex``, used to build an index of ``DescriptorElement`` instances.
The ``rank`` method takes examples of relevant and not-relevant ``DescriptorElement`` examples with which the algorithm uses to rank (think sort) the indexed ``DescriptorElement`` instances by relevancy (on a ``[0, 1]`` scale).
