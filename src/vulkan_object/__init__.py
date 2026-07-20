# Copyright 2025 The Khronos Group Inc.
#
# SPDX-License-Identifier: Apache-2.0

import functools
import importlib.resources
import inspect
import tempfile
import os
from xml.etree import ElementTree

# Use relative imports to access sibling modules
from .reg import Registry
from .base_generator import BaseGenerator, BaseGeneratorOptions, SetOutputDirectory, SetOutputFileName, SetTargetApiName, SetMergedApiNames

# Import the submodule as 'vo_module' to avoid naming conflicts with the VulkanObject class
from . import vulkan_object as vo_module
from .vulkan_object import VulkanObject, CapabilityAlias

# Dynamically collect all classes and TypeAliases defined inside vulkan_object.py
_DYNAMIC_EXPORTS = []
for name, obj in inspect.getmembers(vo_module):
    # Ensure it was actually defined in vulkan_object.py (not imported from enum/dataclasses/etc.)
    if getattr(obj, "__module__", None) == vo_module.__name__:
        globals()[name] = obj
        _DYNAMIC_EXPORTS.append(name)

__all__ = [
    'get_vulkan_object',
    'CapabilityAlias', # is an alias, needs a special export
    *sorted(_DYNAMIC_EXPORTS)
]

# Create the simplified, cached public function
@functools.lru_cache(maxsize=1)
def get_vulkan_object(alternative_xml: str = None, video: bool = False) -> VulkanObject:
    """
    Parses the bundled Vulkan registry (vk.xml) and returns the populated
    VulkanObject.

    This function encapsulates all the setup logic. The result is cached,
    so subsequent calls are instantaneous.

    Args:
        api_name: The API name to parse from the registry, defaults to 'vulkan'.
        alternative_xml: Supply a full path to a different vk.xml (used for testing future extensions)

    Returns:
        An initialized VulkanObject instance providing access to the
        Vulkan API registry data.
    """
    # This dummy generator class is required by the reg.py interface.
    # We don't need it to do anything, as we just want the parsed data object.
    class _InternalGenerator(BaseGenerator):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

        def generate(self):
            # This method is called by reg.apiGen() but we don't need to
            # generate any files, so we just pass. The real goal is to
            # populate self.vk (the VulkanObject).
            pass

    # The original script required setting an output directory, even if
    # it's not used. We'll use a temporary one that cleans itself up.
    with tempfile.TemporaryDirectory() as output_dir:
        SetOutputDirectory(output_dir)
        SetOutputFileName("unused.txt")
        # TODO - Make a get_vulkan_sc_object() or pass this in as a parameter
        SetTargetApiName('vulkan')
        SetMergedApiNames(None)

        xml_path = None

        if alternative_xml:
            if not os.path.isfile(alternative_xml):
                raise FileNotFoundError(f"The provided alternative XML file does not exist or is not a file: {alternative_xml}")
            xml_path = alternative_xml
        else:
            # Try the installed package resource first
            try:
                resource_path = importlib.resources.files('vulkan_object').joinpath('vk.xml')
                if resource_path.is_file():
                    xml_path = str(resource_path)
            except (ImportError, ModuleNotFoundError, TypeError):
                xml_path = None

            # Fallback: Check local development path 'src/vulkan_object/vk.xml'
            if xml_path is None:
                base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                fallback_path = os.path.join(base_dir, 'vulkan_object', 'vk.xml')
                if os.path.exists(fallback_path):
                    xml_path = fallback_path

            if xml_path is None:
                raise RuntimeError("Could not find the bundled vk.xml - something has gone wrong with packaging.")

        video_xml_path = None
        if video:
            video_xml_path = xml_path[:-6] + 'video.xml'

        # Initialize the generator and the registry machinery
        generator = _InternalGenerator()
        base_options = BaseGeneratorOptions(videoXmlPath=video_xml_path)
        reg = Registry(generator, base_options)
        tree = ElementTree.parse(xml_path)
        reg.loadElementTree(tree)

        # This invokes reg.py and will populate _InternalGenerator
        reg.apiGen()

        return generator.vk

