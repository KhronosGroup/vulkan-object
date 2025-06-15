# Vulkan Object Python Package

Parsing the [`vk.xml`](https://github.com/KhronosGroup/Vulkan-Headers/blob/main/registry/vk.xml) in Vulkan is easy, processing it is hard!

It is very easy for people to mess up trying to process the `vk.xml` file, so we created `VulkanObject`

`VulkanObject` is just a python dataclass that is defined in [Vulkan-Headers/registry/vulkan_object.py](https://github.com/KhronosGroup/Vulkan-Headers/blob/main/registry/vulkan_object.py). It uses the [reg.py](https://github.com/KhronosGroup/Vulkan-Headers/blob/main/registry/reg.py) framework that the Vulkan Spec is generated with in order to populate the `VulkanObject` data structure.

This python package makes it **super easy** to get going.

```bash
pip install vulkan-object
```

```python
from vulkan_object import get_vulkan_object, VulkanObject

vk = get_vulkan_object()

print(f'There are now {len([x for x in vk.extensions.values()])} extensions in Vulkan')

print(f'Built with the {vk.headerVersion} headers')
```

## Updating this repo

run `python update.py /path/to/Vulkan-Headers` and it will do everything to sync this package up with the new headers

## Testing locally

To test, grab the repo and go `pip install -e .` in the root directory and will simulate grabbing it from `pip`

## What is this package/repo actually?

The Vulkan-Headers contain a bunch of scripts in the `Vulkan-Headers/registry/` directory that repos can use to help generate code.

The main issue is the delivery mechanism for python projects. This package/repo just grabs the Vulkan-Headers scripts (**not** the C header files themselves!) and make it easier to integrate with projects.