import sys
from colorama import Fore, Style, init
import numpy as np
from numpy._typing import NDArray
import rasterio
from rasterio.transform import from_origin
import os

def checkPara(message: str, idx: int) -> bool:
    if (idx < len(message) - 2):
        if (message[idx + 1] == message[idx + 2] == ':'):
            return True

    return False

def printError(message: str, exit_code: int) -> None:
    n = -1
    for i in range(0, len(message)):
        if (checkPara(message, i)):
            n = i
            break

    if (n != -1):
        print(Fore.RED + message[:n + 1] + Style.RESET_ALL, file=sys.stderr, end="")
        print(message[n + 1:], file=sys.stderr, end="\n")
    else:
        print(Fore.RED + message + Style.RESET_ALL, file=sys.stderr)
    sys.exit(exit_code)

def create_geotiff(data: NDArray[np.float32], filename: str, transform, crs: str) -> None:
    height , width = data.shape
    try:
        with rasterio.open(
                filename, 'w',
                driver='GTiff',
                height=height, width=width,
                count=1, dtype='float32',
                crs=crs,
                transform=transform
                ) as dst:
            dst.write(data, 1)
    except Exception as e:
        raise e


def main() -> None:
    init() # Intializae  @colorama

    # Latitude and Longitude details
    lat_start = 7.5
    lat_step = 1.0
    lon_start = 67.5
    lon_step = 1.0

    # Coordinate Reference System (CRS)
    crs = 'EPSG:4326'  # WGS84

    # Create transform object
    transform = from_origin(lon_start - lon_step / 2, lat_start - lat_step / 2, lat_step, -lon_step)

    # CMD line arguemnet check
    n = len(sys.argv)
    if n != 3:
        printError("Usage:: Grid2Text [filename] [output file]", 1);

    if os.path.isdir(sys.argv[2]) == False:
        print(Fore.YELLOW + "INFO" + Style.RESET_ALL + f":: Directory does not exist: {sys.argv[2]}")
        # print(Fore.GREEN+ "INFO" + Style.RESET_ALL + f":: Creating Directory: " + os.path.join(os.getcwd(), sys.argv[2]))
        # os.makedirs(sys.argv[2])

    """
        Reading the file
    """
    try:
        with open(sys.argv[1], "rb") as file:
            t = np.zeros((31, 31), dtype=np.float32)
            for k in range(366):
                t = np.fromfile(file, dtype=np.float32, count=31 * 31)
                if t.shape[0] == 0:
                    sys.exit(1)

                t = t.reshape((31, 31))


                # if k == 105:
                create_geotiff(t, sys.argv[2] + f"/{os.path.basename(sys.argv[1])}-{k}.tif", transform, crs)

    except FileNotFoundError as e:
        printError(f"Error:: {e}: {sys.argv[1]}", 2)

    except PermissionError as e:
        printError(f"Error:: {e}: {sys.argv[1]}", 2)

    except IOError as e:
        printError(f"Error:: {e}: {sys.argv[1]}", 2);

    except Exception as e:
        printError(f"Error:: unexcepted error {e}: {sys.argv[1]}", 2)


if __name__ == "__main__":
    main()
