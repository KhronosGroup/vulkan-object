# Vulkan Object Python Package

Parsing the [`vk.xml`](https://github.com/KhronosGroup/Vulkan-Headers/blob/main/registry/vk.xml) in Vulkan is easy, processing it is hard!

It is very easy for people to mess up trying to process the `vk.xml` file, so we created `VulkanObject`

`VulkanObject` is just a python dataclass that is defined in [Vulkan-Headers/registry/vulkan_object.py](https://github.com/KhronosGroup/Vulkan-Headers/blob/main/registry/vulkan_object.py). It uses the [reg.py](https://github.com/KhronosGroup/Vulkan-Headers/blob/main/registry/reg.py) framework that the Vulkan Spec is generated with in order to populate the `VulkanObject` data structure.

This python package makes it **super easy** to get going.

```bash
pip install vulkan-object
```

and then it is as simple as

```python
#!/usr/bin/env python3
from vulkan_object import get_vulkan_object

# This builds the VulkanObject that is populated and ready to be used
vk = get_vulkan_object()

print(f'There are now {len([x for x in vk.extensions.values()])} extensions in Vulkan')

print(f'Built with the {vk.headerVersion} headers')

longest_count = 0
for struct in vk.structs.values():
    if len(struct.name) > longest_count:
        longest_count = len(struct.name)
        longest_struct = struct
print(f'Longest Struct name is {longest_struct.name} at {longest_count} characters')
```

## Quick query from the terminal

Just run the following and you can quickly use `vk` in your terminal for some quick query

`python -i -c "from vulkan_object import get_vulkan_object;vk = get_vulkan_object()"`

## More example

[example.py](https://github.com/KhronosGroup/vulkan-object/blob/main/example.py) has more in depth ways to use this

## What is this package/repo actually?

The Vulkan-Headers contain a bunch of scripts in the `Vulkan-Headers/registry/` directory that repos can use to help generate code.

The main issue is the delivery mechanism for python projects. This package/repo just grabs the Vulkan-Headers scripts (**not** the C header files themselves!) and make it easier to integrate with projects.

### Updating this repo

run `python update.py /path/to/Vulkan-Headers` and it will do everything to sync this package up with the new headers