Note: The PyTorch model files cannot be uploaded due to privacy policy, however, the code notebooks have been uploaded in the folder "code_files" for the purpose of training on new data.

This project main objective is to perform OCR on Pakistan National ID Cards for the purpose of verification of customers. However, simply performing OCR using installed libraries was not feasible as accuracy was effected due to image lightning, camera pixel, background and misalignment. Therefore, the project had to go through multiple stages to achieve the objective which as stated below:

1. ID Card Keypoint detection
2. Image Alignment and Rotation 
3. Using GAN for Image Cleaning

An illustration of the above 03 steps before we perform OCR (using easyocr library) is shown below:

![OCR_Process](https://user-images.githubusercontent.com/51902209/230748038-8310cb67-6dfe-45eb-9b51-c777e9328c8b.PNG)

**The work on GAN is inspired by the repository: https://github.com/junyanz/pytorch-CycleGAN-and-pix2pix**

Any input/feedback would be highly-appreciated and incorporated! 

`Authors:  Zain Ispahani (www.github.com/Zain-Ispahani); Muhammad Usman (www.github.com/MuhamaadUsman)`
# OCR Product Suite


## Deployment Instructions
**Manual installation**

1. Clone git repo using provided link
```unix
git clone \\link\to\git
```
1. Change Directory to OCRProductSuite 
```unix
cd OCRProductSuite
```
2. Install Linux Packages from the "Linux\_packages.txt" file.
_# note that these packages are from deb use RPM for RedHat_
3. Install python packages from "requirements.txt" file or run following command.
```unix
pip3 install -r requirments.txt
```
4. Create **gunicorn** server follow the steps in "deploymentdocuments\gunicorn Setup.docx".
5. run application using.
```unix
gunicorn -c configration.ini --worker-tmp-dir ‘/dev/shm’ app:app
```

**Using Docker container (build new image)**
1. Clone git repo using provided link
```unix
git clone \\link\to\git
```
2. Change Directory to OCRProductSuite 
```unix
cd OCRProductSuite
```
3. Build docker images with following command
```unix
sudo docker build -t ocr-api .
```
4. Edit `configuration.ini` as per requirements. _note: do not change below **do not change line**_
5. Run container using following command
```unix
sudo docker run -it -v /Path/to/OCRProductSuite/:/home/code -p 5000:5000 ocr-api
```
- _ `-v` is for mounting directory use multiple `-v` to mount multiple directories_
- _ `-p` is to map ports, left one is host and right is guest (do not change the right one)_

**Using Docker container (pre-built image)**
1. Clone git repo using provided link
```unix
git clone \\link\to\git
```
2. Change Directory to OCRProductSuite 
```unix
cd OCRProductSuite
```
3. load pre-built docker images with following command
```unix
sudo docker load < /path/to/ocr-api.tar
```
4. Run container using following command
```unix
sudo docker run -it -v /Path/to/OCRProductSuite/:/home/code -p 5000:5000 ocr-api
```
- _ `-v` is for mounting directory use multiple `-v` to mount multiple directories_
- _ `-p` is to map ports, left one is host and right is guest (do not change the right one)_

## ☺
