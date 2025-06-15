from vulkan_object import get_vulkan_object, VulkanObject

vk = get_vulkan_object()

print(f'There are now {len([x for x in vk.extensions.values()])} extensions in Vulkan')

print(f'Built with the {vk.headerVersion} headers')