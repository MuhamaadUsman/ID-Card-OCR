from __future__ import print_function, division
import torch
import torch.backends.cudnn as cudnn
from torchvision import transforms

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

class NICRecognizer:
    def __init__(self, model_path):
        self.modelpath = model_path
        self.model_details = torch.load(self.modelpath, map_location=DEVICE)
        self.model = self.model_details['model']
        self.model.load_state_dict(self.model_details['state_dict_model'])
        self.classes = self.model_details['Classes']
        cudnn.benchmark = True
        self.model.to()
        Warning("model loaded successfully")
        # print(self.classes)

    def _transform(self, images):
        preprocess = transforms.Compose([
            transforms.Resize(64),
            transforms.CenterCrop(64),
            transforms.ToTensor(),
            transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5)),
        ])
        transformedimages = preprocess(images).unsqueeze(0)
        # transformedImages
        return transformedimages

    def classify(self, images, num_results):
        transformedImages = self._transform(images)
        with torch.no_grad():
            output = self.model(transformedImages)
        probabilities = torch.nn.functional.softmax(output[0], dim=0)

        top5_prob, top5_catid = torch.topk(probabilities, num_results)
        results = []
        for i in range(top5_prob.size(0)):
            results.append((self.classes[top5_catid[i]], top5_prob[i].item()))
        return results

# Model_load = torch.load()


