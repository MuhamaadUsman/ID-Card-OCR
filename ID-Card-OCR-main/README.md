Note: The PyTorch model files have not been added yet, they will be included later. Also, a few changes to be made in the code which will be ready for production.

`Authors:  Zain Ispahani; Muhammad Usman; Muhammad Ahmad`
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
4. Edit `configuration.ini` as per requirements. _note: do not change blew **do not change line**_
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
4. Edit `configuration.ini` as per requirements. _note: do not change blew **do not change line**_
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
4. Edit `configuration.ini` as per requirements. _note: do not change blew **do not change line**_
4. Run container using following command
```unix
sudo docker run -it -v /Path/to/OCRProductSuite/:/home/code -p 5000:5000 ocr-api
```
- _ `-v` is for mounting directory use multiple `-v` to mount multiple directories_
- _ `-p` is to map ports, left one is host and right is guest (do not change the right one)_

## ☺
