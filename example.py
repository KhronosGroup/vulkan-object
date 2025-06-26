#!/usr/bin/env python3

# Click on 'VulkanObject' with your IDE/TextEditor to see VulkanObject definition
# https://github.com/KhronosGroup/Vulkan-Headers/blob/main/registry/vulkan_object.py
from vulkan_object import get_vulkan_object, VulkanObject

vk = get_vulkan_object()

# Example 1
global_functions = []
for command in vk.commands.values():
    if command.params[0].type not in vk.handles:
        global_functions.append(command.name)
print(f'Global functions are {global_functions}')

print("\n----------------------------------------------------\n")

# Example 2
print("VK_KHR_dynamic_rendering_local_read added the following commands")
extension = vk.extensions['VK_KHR_dynamic_rendering_local_read']
for command in [x for x in extension.commands]:
    print(f'- {command.name}')

print("\n----------------------------------------------------\n")

# Example 3
struct = vk.structs['VkImageSubresource2']
print(f'VkImageSubresource2 also is known as {struct.aliases}')
print(f'Members are {[x.name for x in struct.members]}')
# use base type to get the next struct's info
struct = vk.structs[struct.members[2].type]
print(f'VkImageSubresource also is known as {struct.aliases}')
print(f'Members are {[x.name for x in struct.members]}')

print("\n----------------------------------------------------\n")

# Example 4
formats = [x for x in vk.formats.values() if x.compressed]
print(f'There are {len(formats)} compressed formats')
formats = [x for x in formats if x.blockSize == 8]
print(f'{len(formats)} have a block size of 8')
formats = [x for x in formats if x.blockExtent == ['4', '4', '1']]
print(f'{len(formats)} have a block extent of 4x4x1')
formats = "\n\t".join([x.name for x in formats])
print(f'They are:\n\t{formats}')
