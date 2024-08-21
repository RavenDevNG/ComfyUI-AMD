import os
import re
import logging
from typing import Callable, Optional


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def replace_function_in_file(file_path: str, function_name: str, new_function: str) -> None:
    """
    Replace a function in a file with a new implementation.

    Args:
        file_path (str): Path to the file.
        function_name (str): Name of the function to replace.
        new_function (str): New function implementation.

    Raises:
        FileNotFoundError: If the file is not found.
        PermissionError: If there's no permission to read/write the file.
    """
    try:
        with open(file_path, 'r') as file:
            content = file.read()

        old_function_pattern = rf'def {function_name}\(.*?\):.*?(?=\n\S)'
        new_content = re.sub(old_function_pattern, new_function, content, flags=re.DOTALL)

        if new_content != content:
            with open(file_path, 'w') as file:
                file.write(new_content)
            logger.info(f"Function {function_name}() has been updated in file: {file_path}")
        else:
            logger.warning(f"Function {function_name}() not found for update in file: {file_path}")
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
    except PermissionError:
        logger.error(f"Permission denied: {file_path}")
    except Exception as e:
        logger.error(f"An error occurred while processing {file_path}: {str(e)}")

def update_file(file_path: str, updates: dict[str, str]) -> None:
    """
    Update multiple functions in a file.

    Args:
        file_path (str): Path to the file.
        updates (dict): Dictionary of function names and their new implementations.
    """
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return

    for function_name, new_function in updates.items():
        replace_function_in_file(file_path, function_name, new_function)

def main():
    current_dir = os.getcwd()

    # New function definitions
    new_functions = {
        "get_torch_device_name": '''def get_torch_device_name(device):
    if hasattr(device, 'type'):
        if device.type == "cuda":
            try:
                allocator_backend = torch.cuda.get_allocator_backend()
            except:
                allocator_backend = ""
            return "{} {} : {}".format(device, torch.cuda.get_device_name(device), allocator_backend)
        else:
            return "{}".format(device.type)
    elif is_intel_xpu():
        return "{} {}".format(device, torch.xpu.get_device_name(device))
    else:
        return "CUDA {}: {}".format(device, torch.cuda.get_device_name(device))
try:
    torch_device_name = get_torch_device_name(get_torch_device())
    if "[ZLUDA]" in torch_device_name:
        print("***--------------------------------ZLUDA------------------------------------***")
        print("Detected ZLUDA, support for it is experimental and comfy may not work properly.")
        if torch.backends.cudnn.enabled:
            torch.backends.cudnn.enabled = False
            print("Disabling cuDNN because ZLUDA does currently not support it.")
        torch.backends.cuda.enable_flash_sdp(False)
        print("Disabling flash because ZLUDA does currently not support it.")
        torch.backends.cuda.enable_math_sdp(True)
        print("Enabling math_sdp.")
        torch.backends.cuda.enable_mem_efficient_sdp(False)
        print("Disabling mem_efficient_sdp because ZLUDA does currently not support it.")
        print("***-------------------------------------------------------------------------***")
    print("Device:", torch_device_name)
except:
    print("Could not pick default device.")''',

        "cuda_malloc_supported": '''def cuda_malloc_supported():
    try:
        names = get_gpu_names()
    except:
        names = set()
    for x in names:
        if "AMD" in x:
            return False
        elif "NVIDIA" in x:
            for b in blacklist:
                if b in x:
                    return False
    return False
#We don't need malloc at all with amd gpu's. So disabling all together'''
    }

    # Update model_management.py in the comfy directory
    comfy_dir = os.path.join(current_dir, "comfy")
    model_management_path = os.path.join(comfy_dir, "model_management.py")
    update_file(model_management_path, {"get_torch_device_name": new_functions["get_torch_device_name"]})

    # Update cuda_malloc.py in the current directory
    cuda_malloc_path = os.path.join(current_dir, "cuda_malloc.py")
    update_file(cuda_malloc_path, {"cuda_malloc_supported": new_functions["cuda_malloc_supported"]})

if __name__ == "__main__":
    main()
