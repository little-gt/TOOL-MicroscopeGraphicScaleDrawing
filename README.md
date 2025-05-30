>  编译的版本可以在 release 处下载，可以选择下载英文版或者中文版。
>  The compiled version can be downloaded from the release, either in English or Chinese.

---

## 中文指南 (Chinese Guide)

### 功能特点

*   **批量导入图片：** 一次性轻松导入多个图片文件。
*   **图片列表与缩略图：** 在可滚动的列表中查看所有导入的图片，并带有小预览图。
*   **单张图片配置：**
    *   设置放大倍数。
    *   定义图片标定宽度（在给定放大倍数下，显微镜视野在屏幕/传感器上对应的实际宽度，单位cm）。
    *   选择比例尺位置（左下或右下）。
    *   添加样品名称。
    *   添加拍摄时间。
    *   在比例尺旁添加自定义备注。
    *   自定义文字颜色和比例尺颜色。
*   **实时预览：** 实时查看所选图片应用注释后的效果。
*   **自动计算比例尺：** 工具会根据放大倍数和图片尺寸智能计算合适的比例尺长度。
*   **读取元数据：** 尝试从图片的EXIF数据中读取放大倍数。
*   **批量应用设置：** 将当前主面板的设置应用到多个选定的图片。
*   **批量处理与导出：** 处理所有已配置的图片，并将它们保存到指定的输出文件夹。
*   **字体处理：** 包含查找合适的中日韩（CJK）字体用于注释的逻辑。

### 软件截图

1.  **初始界面与导入图片：**
    应用程序启动后界面简洁。点击“导入图片”按钮选择您的图片文件。
    ![步骤1：导入图片](/screenshots/step1.png)

2.  **图片配置与预览：**
    导入图片后，图片会显示在左侧的“图片列表”中。
    *   在列表中单击一张图片以选中并进行编辑。
    *   在列表下方的输入框中填写“放大倍数”、“图片标定宽度(cm)”、“样品名称”等参数。
    *   右侧主区域会实时显示所选图片应用当前注释后的预览效果。
    ![步骤2：配置图片](/screenshots/step2.png)

3.  **批量应用设置：**
    点击“批量运用到图片”按钮打开一个对话框。
    *   在此处，您可以从列表中选择多张图片，以应用主面板当前的设置。
    *   这对于将通用设置（例如，屏幕宽度、文本颜色）快速应用到一组图片非常有用。
    ![步骤3：批量应用设置](/screenshots/step3.png)

### 使用说明

1.  **导入图片：** 点击“导入图片”按钮。选择一个或多个图片文件（支持JPG, PNG, TIFF格式）。
2.  **选择图片：** 在左侧面板的“图片列表”中点击一张图片。
3.  **配置参数：**
    *   调整“放大倍数”。
    *   设置“图片标定宽度(cm)”—— 这是您的显微镜在该放大倍数下，视野在屏幕/传感器上代表的实际宽度。
    *   选择“标尺位置”：“左下”或“右下”。
    *   按需填写“样品名称”、“拍摄时间”和“比例尺旁备注”。
    *   点击“文字颜色”和“标尺颜色”旁边的“选择”按钮来挑选颜色。
    *   右侧的预览会自动更新。
4.  **（可选）批量应用设置：**
    *   根据需要在主面板中配置好设置。
    *   点击“批量运用到图片”按钮。
    *   在弹出的对话框中，勾选您想要应用这些设置的图片。
    *   点击“应用选中”。
5.  **选择导出文件夹：** 点击“选择导出文件夹”按钮，并为处理后的图片选择一个目录。
6.  **处理图片：** 点击“开始批量处理”按钮。应用程序将使用每张图片的特定设置来处理它，并保存到导出文件夹。

### 安装与运行

1.  **先决条件：**
    *   Python 3.x
2.  **安装依赖：**
    ```bash
    pip install Pillow customtkinter CTkMessagebox matplotlib
    ```
3.  **运行应用程序：**
    将提供的 Python 代码保存为 `.py` 文件（例如 `sem_annotator_cn.py`），然后从终端运行它：
    ```bash
    python sem_annotator.py
    ```

### 注意事项
*   **字体：** 脚本会尝试查找合适的中文字体（如黑体、微软雅黑等）。如果中文字符显示为方框或乱码，请确保您的系统安装了这些常用中文字体。
*   **元数据：** 从图片元数据中读取放大倍数的功能会尽力尝试，但并非所有图片都包含或以标准格式包含此信息。如果未能读取，请手动输入。

---

## English Guide

### Features

*   **Batch Image Import:** Easily import multiple image files at once.
*   **Image List with Thumbnails:** View all imported images in a scrollable list with small previews.
*   **Individual Image Configuration:**
    *   Set magnification.
    *   Define image calibration width (screen width in cm for the given magnification).
    *   Choose scale bar position (left-bottom or right-bottom).
    *   Add sample name.
    *   Add shooting time.
    *   Add custom remarks next to the scale bar.
    *   Customize text color and scale bar color.
*   **Live Preview:** See a real-time preview of the selected image with applied annotations.
*   **Automatic Scale Bar Calculation:** The tool intelligently calculates an appropriate scale bar length based on magnification and image dimensions.
*   **Metadata Reading:** Attempts to read magnification from image EXIF data.
*   **Batch Apply Settings:** Apply the current main panel settings to multiple selected images.
*   **Batch Processing & Export:** Process all configured images and save them to a specified output folder.
*   **Font Handling:** Includes logic to find suitable CJK (Chinese, Japanese, Korean) fonts for annotations.

### Screenshots

1.  **Initial Interface & Importing Images:**
    The application starts with a clean interface. Click "导入图片" (Import Images) to select your image files.
    ![Step 1: Import Images](/screenshots/step1.png)

2.  **Image Configuration & Preview:**
    After importing, images appear in the "图片列表" (Image List) on the left.
    *   Click an image in the list to select it for editing.
    *   Input parameters like "放大倍数" (Magnification), "图片标定宽度(cm)" (Image Calibration Width), "样品名称" (Sample Name), etc., in the fields below the list.
    *   The main area on the right shows a live preview of the selected image with the current annotations.
    *   The text "双击切换，每个图片的配置单独存" means "Double-click to switch, each image's configuration is saved separately".
    *   "请输入你所拍摄图片的显微镜的参数，一般在说明书上" means "Please enter the parameters of the microscope you used to take the picture, usually found in the manual."
    *   "批量运用点这个" points to the "批量运用到图片" (Batch Apply to Images) button.
    ![Step 2: Configure Image](/screenshots/step2.png)

3.  **Batch Applying Settings:**
    Click "批量运用到图片" (Batch Apply to Images) to open a dialog.
    *   Here, you can select multiple images from the list to apply the current settings from the main panel.
    *   This is useful for applying common settings (e.g., screen width, text color) to a group of images quickly.
    ![Step 3: Batch Apply Settings](/screenshots/step3.png)

### How to Use

1.  **Import Images:** Click the "导入图片" (Import Images) button. Select one or more image files (JPG, PNG, TIFF supported).
2.  **Select an Image:** Click on an image in the "图片列表" (Image List) on the left panel.
3.  **Configure Parameters:**
    *   Adjust "放大倍数" (Magnification).
    *   Set "图片标定宽度(cm)" (Image Calibration Width in cm) - this is the actual width your microscope's field of view represents on its screen/sensor at the given magnification.
    *   Choose "标尺位置" (Scalebar Position): "左下" (Left Bottom) or "右下" (Right Bottom).
    *   Fill in "样品名称" (Sample Name), "拍摄时间" (Shooting Time), and "比例尺旁备注" (Remark next to scalebar) as needed.
    *   Click "选择" (Select) next to "文字颜色" (Text Color) and "标尺颜色" (Scalebar Color) to pick colors.
    *   The preview on the right will update automatically.
4.  **(Optional) Batch Apply Settings:**
    *   Configure the settings in the main panel as desired.
    *   Click "批量运用到图片" (Batch Apply to Images).
    *   In the dialog, check the images you want to apply these settings to.
    *   Click "应用选中" (Apply to Selected).
5.  **Select Export Folder:** Click "选择导出文件夹" (Select Export Folder) and choose a directory for the processed images.
6.  **Process Images:** Click "开始批量处理" (Start Batch Processing). The application will process each image with its specific settings and save it to the export folder.

### Installation and Running

1.  **Prerequisites:**
    *   Python 3.x
2.  **Install Dependencies:**
    ```bash
    pip install Pillow customtkinter CTkMessagebox matplotlib
    ```
3.  **Run the Application:**
    Save the provided Python code as a `.py` file (e.g., `sem_annotator_en.py`) and run it from your terminal:
    ```bash
    python sem_annotator.py
    ```