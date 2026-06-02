
from flask import Flask, render_template_string, request, send_file
from PIL import Image, ImageOps
import os
import math
import uuid
import zipfile

app = Flask(__name__)

generated_files = {}

# =========================================================
# HTML UI
# =========================================================

HTML = """

<!DOCTYPE html>

<html>

<head>

<title>Professional Photo PDF Generator</title>

<meta name="viewport" content="width=device-width, initial-scale=1.0">

<style>

*{
    margin:0;
    padding:0;
    box-sizing:border-box;
}

body{

    font-family:Arial,sans-serif;

    background:
    linear-gradient(
        135deg,
        #0f172a,
        #1e293b
    );

    min-height:100vh;

    display:flex;
    justify-content:center;
    align-items:center;

    padding:20px;
}

.container{

    width:100%;
    max-width:750px;

    background:white;

    padding:40px;

    border-radius:24px;

    box-shadow:
    0 20px 60px rgba(0,0,0,0.35);
}

.title{

    text-align:center;

    font-size:36px;

    font-weight:bold;

    margin-bottom:12px;

    color:#111827;
}

.subtitle{

    text-align:center;

    color:#6b7280;

    line-height:1.7;

    margin-bottom:35px;

    font-size:16px;
}

.upload-box{

    border:2px dashed #cbd5e1;

    border-radius:18px;

    padding:35px;

    text-align:center;

    background:#f8fafc;

    transition:0.3s;
}

.upload-box:hover{

    border-color:#2563eb;

    background:#eff6ff;
}

.upload-icon{

    font-size:60px;

    margin-bottom:15px;
}

input[type=file]{

    margin-top:20px;

    width:100%;

    font-size:16px;
}

.input-group{

    margin-top:25px;
}

.input{

    width:100%;

    padding:16px;

    border-radius:14px;

    border:1px solid #d1d5db;

    font-size:16px;

    outline:none;
}

.input:focus{

    border-color:#2563eb;
}

.submit-btn{

    width:100%;

    margin-top:30px;

    padding:18px;

    border:none;

    border-radius:16px;

    background:#2563eb;

    color:white;

    font-size:20px;

    font-weight:bold;

    cursor:pointer;

    transition:0.3s;
}

.submit-btn:hover{

    background:#1d4ed8;
}

.submit-btn:disabled{

    background:gray;

    cursor:not-allowed;
}

.download-btn{

    width:100%;

    margin-top:25px;

    padding:18px;

    border:none;

    border-radius:16px;

    background:#16a34a;

    color:white;

    font-size:20px;

    font-weight:bold;

    text-decoration:none;

    display:block;

    text-align:center;
}

.file-item{

    background:#eff6ff;

    padding:15px;

    border-radius:12px;

    margin-top:12px;

    display:flex;

    justify-content:space-between;

    align-items:center;
}

.file-name{

    font-weight:bold;

    color:#1e3a8a;

    word-break:break-all;
}

.remove-btn{

    background:red;

    color:white;

    border:none;

    padding:8px 14px;

    border-radius:8px;

    cursor:pointer;
}

.total-box{

    margin-top:20px;

    background:#dcfce7;

    padding:15px;

    border-radius:12px;

    text-align:center;

    font-weight:bold;

    color:#166534;
}

.footer{

    margin-top:35px;

    text-align:center;

    color:#6b7280;

    line-height:1.8;
}

/* ====================================================== */
/* LOADING SCREEN */
/* ====================================================== */

#loading-screen{

    position:fixed;

    top:0;
    left:0;

    width:100%;
    height:100%;

    background:
    rgba(15,23,42,0.92);

    backdrop-filter:blur(6px);

    display:none;

    justify-content:center;
    align-items:center;

    z-index:99999;
}

.loader-box{

    background:white;

    padding:50px;

    border-radius:24px;

    text-align:center;

    width:360px;

    box-shadow:
    0 20px 60px rgba(0,0,0,0.4);
}

.spinner{

    width:85px;
    height:85px;

    border:8px solid #dbeafe;

    border-top:8px solid #2563eb;

    border-radius:50%;

    margin:auto;

    animation:spin 1s linear infinite;
}

@keyframes spin{

    100%{
        transform:rotate(360deg);
    }

}

.loading-title{

    margin-top:25px;

    font-size:30px;

    font-weight:bold;

    color:#111827;
}

.loading-subtitle{

    margin-top:12px;

    color:#6b7280;

    line-height:1.6;
}

#countdown{

    margin-top:25px;

    background:#eff6ff;

    padding:18px;

    border-radius:14px;

    font-size:24px;

    font-weight:bold;

    color:#1d4ed8;
}

</style>

</head>

<body>

<div class="container">

<div class="title">
Photo PDF Generator
</div>

<div class="subtitle">

Upload multiple ZIP files.<br>

All photos will combine into one professional PDF.

</div>

<form
method="POST"
enctype="multipart/form-data"
id="uploadForm"
>

<div class="upload-box">

<div class="upload-icon">
📁
</div>

<h3>
Upload ZIP Files
</h3>

<input
type="file"
id="zipfiles"
accept=".zip"
multiple
required
>

<div id="file-list"></div>

<div id="total-count"></div>

</div>

<div class="input-group">

<input
class="input"
type="text"
name="pdfname"
placeholder="Enter PDF Name"
required
>

</div>

<button
class="submit-btn"
type="submit"
>

Generate PDF

</button>

</form>

DOWNLOAD_BUTTON

<div class="footer">

✔ Multiple ZIP Upload<br>
✔ Shows Uploaded File List<br>
✔ Remove Files Option<br>
✔ Loading Animation + Timer<br>
✔ 25 Photos Per Page

</div>

</div>

<!-- ===================================================== -->
<!-- LOADING SCREEN -->
<!-- ===================================================== -->

<div id="loading-screen">

<div class="loader-box">

<div class="spinner"></div>

<div class="loading-title">
Generating PDF
</div>

<div class="loading-subtitle">
Please wait while processing images
</div>

<div id="countdown">
Estimated Time: 120 sec
</div>

</div>

</div>

<script>

let allFiles = [];

const fileInput =
    document.getElementById(
        "zipfiles"
    );

const fileList =
    document.getElementById(
        "file-list"
    );

const totalCount =
    document.getElementById(
        "total-count"
    );

fileInput.addEventListener(
    "change",
    function(event){

        const selected =
            Array.from(
                event.target.files
            );

        selected.forEach(file => {

            const exists =
                allFiles.some(
                    f => f.name === file.name
                );

            if(!exists){

                allFiles.push(file);

            }

        });

        renderFiles();

    }
);

function renderFiles(){

    fileList.innerHTML = "";

    allFiles.forEach((file,index)=>{

        const item =
            document.createElement("div");

        item.className =
            "file-item";

        item.innerHTML = `

        <div class="file-name">

        📁 ${file.name}

        </div>

        <button
        type="button"
        class="remove-btn"
        onclick="removeFile(${index})"
        >

        Remove

        </button>

        `;

        fileList.appendChild(item);

    });

    totalCount.innerHTML = `

    <div class="total-box">

    Total Uploaded ZIP Files:
    ${allFiles.length}

    </div>

    `;

}

function removeFile(index){

    allFiles.splice(index,1);

    renderFiles();

}

document.getElementById(
    "uploadForm"
).addEventListener(
    "submit",
    function(e){

        e.preventDefault();

        if(allFiles.length === 0){

            alert(
                "Please upload ZIP files"
            );

            return;
        }

        // SHOW LOADING SCREEN

        document.getElementById(
            "loading-screen"
        ).style.display = "flex";

        // DISABLE BUTTON

        document.querySelector(
            ".submit-btn"
        ).disabled = true;

        // TIMER

        let seconds = 120;

        const countdown =
            document.getElementById(
                "countdown"
            );

        const timer =
            setInterval(function(){

                seconds--;

                let mins =
                    Math.floor(
                        seconds / 60
                    );

                let secs =
                    seconds % 60;

                countdown.innerHTML =

                    "Estimated Time: " +

                    mins +

                    " min " +

                    secs +

                    " sec";

                if(seconds <= 0){

                    clearInterval(timer);

                    countdown.innerHTML =
                        "Finalizing PDF...";

                }

            },1000);

        // SEND FORM

        const formData =
            new FormData();

        allFiles.forEach(file => {

            formData.append(
                "zipfiles",
                file
            );

        });

        const pdfName =
            document.querySelector(
                'input[name="pdfname"]'
            ).value;

        formData.append(
            "pdfname",
            pdfName
        );

        fetch("/",{
            method:"POST",
            body:formData
        })
        .then(res => res.text())
        .then(data => {

            document.open();
            document.write(data);
            document.close();

        });

    }
);

</script>

</body>

</html>

"""

# =========================================================
# HOME
# =========================================================

@app.route("/", methods=["GET", "POST"])

def home():

    if request.method == "POST":

        try:

            uploaded_files = request.files.getlist(
                "zipfiles"
            )

            pdf_name = request.form["pdfname"]

            unique_id = str(uuid.uuid4())

            temp_folder = os.path.join(
                os.getcwd(),
                f"temp_{unique_id}"
            )

            os.makedirs(
                temp_folder,
                exist_ok=True
            )

            extract_folder = os.path.join(
                temp_folder,
                "photos"
            )

            os.makedirs(
                extract_folder,
                exist_ok=True
            )

            # =====================================================
            # EXTRACT ZIP FILES
            # =====================================================

            for index, uploaded_file in enumerate(
                uploaded_files
            ):

                zip_path = os.path.join(
                    temp_folder,
                    f"zip_{index}.zip"
                )

                uploaded_file.save(zip_path)

                sub_folder = os.path.join(
                    extract_folder,
                    f"folder_{index}"
                )

                os.makedirs(
                    sub_folder,
                    exist_ok=True
                )

                with zipfile.ZipFile(
                    zip_path,
                    "r"
                ) as zip_ref:

                    zip_ref.extractall(
                        sub_folder
                    )

            """
            # =====================================================
            # EXACT LAYOUT (MM)
            # =====================================================

            PAGE_WIDTH_MM = 482.6
            PAGE_HEIGHT_MM = 330.2

            CARD_WIDTH_MM = 85
            CARD_HEIGHT_MM = 55

            COLS = 5
            ROWS = 5

            MAX_PER_PAGE = 25

            # =====================================================
            # GRID SIZE
            # =====================================================

            GRID_WIDTH_MM = CARD_WIDTH_MM * COLS
            GRID_HEIGHT_MM = CARD_HEIGHT_MM * ROWS

            # 425 mm
            # 275 mm

            # =====================================================
            # CENTER MARGINS
            # =====================================================

            LEFT_MARGIN_MM = (
                PAGE_WIDTH_MM -
                GRID_WIDTH_MM
            ) / 2

            RIGHT_MARGIN_MM = LEFT_MARGIN_MM

            TOP_MARGIN_MM = (
                PAGE_HEIGHT_MM -
                GRID_HEIGHT_MM
            ) / 2

            BOTTOM_MARGIN_MM = TOP_MARGIN_MM

            # =====================================================
            # DPI CONVERSION
            # =====================================================

            DPI = 300

            PAGE_WIDTH = int(
                PAGE_WIDTH_MM / 25.4 * DPI
            )

            PAGE_HEIGHT = int(
                PAGE_HEIGHT_MM / 25.4 * DPI
            )

            PHOTO_WIDTH = int(
                CARD_WIDTH_MM / 25.4 * DPI
            )

            PHOTO_HEIGHT = int(
                CARD_HEIGHT_MM / 25.4 * DPI
            )

            LEFT_MARGIN = int(
                LEFT_MARGIN_MM / 25.4 * DPI
            )

            TOP_MARGIN = int(
                TOP_MARGIN_MM / 25.4 * DPI
            ) 
            """
            # =====================================================
            # EXACT PAGE SETTINGS
            # =====================================================

            
#----------------------------------------------------
            """PAGE_WIDTH_MM = 482.6
            PAGE_HEIGHT_MM = 330.2"""

            """PAGE_WIDTH_INCH = 19
            PAGE_HEIGHT_INCH = 13

            CARD_WIDTH_MM = 85
            CARD_HEIGHT_MM = 55

            COLS = 5
            ROWS = 5

            MAX_PER_PAGE = 25

            # =====================================================
            # CONVERT MM TO PIXELS
            # =====================================================

            PAGE_WIDTH = int(
                PAGE_WIDTH_MM / 25.4 * DPI
            )

            PAGE_HEIGHT = int(
                PAGE_HEIGHT_MM / 25.4 * DPI
            )

            PHOTO_WIDTH = int(
                CARD_WIDTH_MM / 25.4 * DPI
            )

            PHOTO_HEIGHT = int(
                CARD_HEIGHT_MM / 25.4 * DPI
            )

            # =====================================================
            # PERFECT CENTER MARGINS
            # =====================================================

            LEFT_MARGIN_MM = 28.8
            TOP_MARGIN_MM = 27.6

            LEFT_MARGIN = int(
                LEFT_MARGIN_MM / 25.4 * DPI
            )

            TOP_MARGIN = int(
                TOP_MARGIN_MM / 25.4 * DPI
            )"""

            # =====================================================
# PAGE SETTINGS
# =====================================================

            DPI = 300

            PAGE_WIDTH_INCH = 19
            PAGE_HEIGHT_INCH = 13

            PAGE_WIDTH = int(PAGE_WIDTH_INCH * DPI)
            PAGE_HEIGHT = int(PAGE_HEIGHT_INCH * DPI)

            # =====================================================
            # CARD SIZE
            # =====================================================

            CARD_WIDTH_MM = 85
            CARD_HEIGHT_MM = 55

            PHOTO_WIDTH = int((CARD_WIDTH_MM / 25.4) * DPI)
            PHOTO_HEIGHT = int((CARD_HEIGHT_MM / 25.4) * DPI)

            # =====================================================
            # GRID
            # =====================================================

            COLS = 5
            ROWS = 5

            MAX_PER_PAGE = 25

            # =====================================================
            # CENTER MARGINS
            # =====================================================

            LEFT_MARGIN_MM = 28.8
            TOP_MARGIN_MM = 27.6

            LEFT_MARGIN = int((LEFT_MARGIN_MM / 25.4) * DPI)
            TOP_MARGIN = int((TOP_MARGIN_MM / 25.4) * DPI)
            


            SUPPORTED = (
                ".jpg",
                ".jpeg",
                ".png",
                ".bmp",
                ".webp"
            )

            # =====================================================
            # LOAD IMAGES
            # =====================================================

            image_files = []

            for root, dirs, files in os.walk(
                extract_folder
            ):

                for file in files:

                    if file.lower().endswith(
                        SUPPORTED
                    ):

                        image_files.append(
                            os.path.join(
                                root,
                                file
                            )
                        )

            image_files.sort()

            if len(image_files) == 0:

                return "No images found."

            # =====================================================
            # CREATE PAGES
            # =====================================================

            total_pages = math.ceil(
                len(image_files)
                / MAX_PER_PAGE
            )

            pdf_pages = []

            for page_number in range(total_pages):

                page = Image.new(
                    "RGB",
                    (
                        PAGE_WIDTH,
                        PAGE_HEIGHT
                    ),
                    "white"
                )

                start = page_number * MAX_PER_PAGE

                end = start + MAX_PER_PAGE

                current = image_files[start:end]

                for index, image_path in enumerate(
                    current
                ):

                    try:

                        img = Image.open(
                            image_path
                        ).convert("RGB")

                        img = ImageOps.fit(
                            img,
                            (PHOTO_WIDTH, PHOTO_HEIGHT),
                            method=Image.Resampling.LANCZOS
                        )

                        canvas = Image.new(
                            "RGB",
                            (
                                PHOTO_WIDTH,
                                PHOTO_HEIGHT
                            ),
                            "white"
                        )

                        x_offset = (
                            PHOTO_WIDTH -
                            img.width
                        ) // 2

                        y_offset = (
                            PHOTO_HEIGHT -
                            img.height
                        ) // 2

                        canvas.paste(
                            img,
                            (
                                x_offset,
                                y_offset
                            )
                        )

                        row = index // COLS
                        col = index % COLS

                        x = LEFT_MARGIN + (
                            col * PHOTO_WIDTH
                        )

                        y = TOP_MARGIN + (
                            row * PHOTO_HEIGHT
                        )

                        page.paste(
                            canvas,
                            (x,y)
                        )

                    except Exception as image_error:

                        print(image_error)

                pdf_pages.append(page)

            # =====================================================
            # SAVE PDF
            # =====================================================

            output_folder = os.path.join(
                os.getcwd(),
                "generated_pdfs"
            )

            os.makedirs(
                output_folder,
                exist_ok=True
            )

            output_pdf = os.path.join(
                output_folder,
                f"{pdf_name}.pdf"
            )

            rgb_pages = []

            for p in pdf_pages:

                rgb_pages.append(
                    p.convert("RGB")
                )

            rgb_pages[0].save(
                output_pdf,
                "PDF",
                resolution=300.0,
                save_all=True,
                append_images=rgb_pages[1:]
            )

            generated_files[unique_id] = output_pdf

            download_button = f'''

            <a
            class="download-btn"
            href="/download/{unique_id}">

            Download PDF

            </a>

            '''

            return render_template_string(
                HTML.replace(
                    "DOWNLOAD_BUTTON",
                    download_button
                )
            )

        except Exception as e:

            return f"<h2>Error:</h2><pre>{str(e)}</pre>"

    return render_template_string(
        HTML.replace(
            "DOWNLOAD_BUTTON",
            ""
        )
    )

# =========================================================
# DOWNLOAD
# =========================================================

@app.route("/download/<file_id>")

def download(file_id):

    file_path = generated_files.get(file_id)

    if not file_path:

        return "File not found."

    if not os.path.exists(file_path):

        return "PDF missing."

    return send_file(
        file_path,
        as_attachment=True
    )

# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    app.run(debug=True)