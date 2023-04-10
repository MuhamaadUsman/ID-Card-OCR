import torch
import torchvision
import torchvision.transforms as transforms
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")



class KeyPoint_Detector:
    def __init__(self, model_path):
        self.model_path = model_path
        self.checkpoint = torch.load(model_path, map_location=torch.device(DEVICE))
        self.model = torchvision.models.detection.keypointrcnn_resnet50_fpn(pretrained=True,
                                                                       pretrained_backbone=True,
                                                                       num_keypoints=17,
                                                                       num_classes=2)
        self.model.load_state_dict(self.checkpoint['model_state_dict'])
        Warning("model loaded successfully")


    def getKeyPoints(self, Image):
        self.model.eval()
        trans = transforms.Compose([transforms.ToTensor()])
        ten_img = trans(Image)
        with torch.no_grad():
            prediction = self.model([ten_img.to(torch.device(DEVICE))])
        return prediction

