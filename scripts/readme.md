# AI Utilities

## Setup Instructions

### 1. **Create a Conda Environment**
To set up the project environment, follow these steps:

1. **Create the Conda Environment:**
   
   If you have a `requirements.txt` file:
   ```bash
   conda create --name mlx --file requirements.txt
   ```

### 2. **Using the `guess_and_rename_png_files.py` Script**
This script processes and renames PNG files in a specified directory.

#### Usage:
```bash
python guess_and_rename_png_files.py <directory_path>
```

Replace `<directory_path>` with the path to the directory containing the PNG files you want to process and rename.

Example:
```bash
python guess_and_rename_png_files.py ./images
```
