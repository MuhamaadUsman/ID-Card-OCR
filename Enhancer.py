from __future__ import print_function, division
import torch
import torch.nn as nn
import torch.backends.cudnn as cudnn
from torchvision import transforms
from PIL import Image
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


class ResnetBlock(nn.Module):

    def __init__(self, dim, padding_type, norm_layer, use_dropout):
        super(ResnetBlock, self).__init__()
        self.conv_block = self.build_conv_block(dim, padding_type, norm_layer, use_dropout)

    def build_conv_block(self, dim, norm_layer, use_dropout, use_bias):
        conv_block = []
        p = 0

        conv_block += [nn.ReflectionPad2d(1)]

        conv_block += [nn.Conv2d(dim, dim, kernel_size=3, padding=p, bias=use_bias), norm_layer(dim), nn.ReLU(True)]

        if use_dropout:
            conv_block += [nn.Dropout(0.5)]

        p = 0

        conv_block += [nn.ReflectionPad2d(1)]

        conv_block += [nn.Conv2d(dim, dim, kernel_size=3, padding=p, bias=use_bias), norm_layer(dim)]

        return nn.Sequential(*conv_block)

    def forward(self, x):
        out = x + self.conv_block(x)  # add skip connections

        return out

class ResnetGenerator(nn.Module):

    def __init__(self, input_nc, output_nc, ngf=64, norm_layer=nn.BatchNorm2d, use_dropout=True, n_blocks=9,
                 padding_type='reflect'):

        assert (n_blocks >= 0)
        super(ResnetGenerator, self).__init__()

        use_bias = False

        model = [nn.ReflectionPad2d(3),
                 nn.Conv2d(input_nc, ngf, kernel_size=7, padding=0, bias=use_bias),
                 norm_layer(ngf),
                 nn.ReLU(True)]

        n_downsampling = 2
        for i in range(n_downsampling):  # add downsampling layers
            mult = 2 ** i
            model += [nn.Conv2d(ngf * mult, ngf * mult * 2, kernel_size=3, stride=2, padding=1, bias=use_bias),
                      norm_layer(ngf * mult * 2),
                      nn.ReLU(True)]

        mult = 2 ** n_downsampling
        for i in range(n_blocks):  # add ResNet blocks

            model += [ResnetBlock(ngf * mult, padding_type=padding_type, norm_layer=norm_layer, use_dropout=use_dropout)]

        for i in range(n_downsampling):  # add upsampling layers
            mult = 2 ** (n_downsampling - i)
            model += [nn.ConvTranspose2d(ngf * mult, int(ngf * mult / 2),
                                         kernel_size=3, stride=2,
                                         padding=1, output_padding=1,
                                         bias=use_bias),
                      norm_layer(int(ngf * mult / 2)),
                      nn.ReLU(True)]
        model += [nn.ReflectionPad2d(3)]
        model += [nn.Conv2d(ngf, output_nc, kernel_size=7, padding=0)]
        model += [nn.Tanh()]

        self.model = nn.Sequential(*model)

    def forward(self, input):

        return self.model(input)


class Enhancer:
    def __init__(self, model_path):
        self.modelpath = model_path
        self.model_details = torch.load(self.modelpath, map_location=DEVICE)
        self.model = self.model_details['model']
        self.model.load_state_dict(self.model_details['state_dict_model'])
        cudnn.benchmark = True
        self.model.eval()
        Warning("model loaded successfully")

    def __make_power_2__(self, img, base, method=Image.BICUBIC):
        ow, oh = img.size
        h = int(round(oh / base) * base)
        w = int(round(ow / base) * base)

        if h == oh and w == ow:
            return img

        return img.resize((w, h), method)

    def _transform(self, images):
        preprocess = transforms.Compose([
            transforms.Lambda(lambda img: self.__make_power_2__(img, base=4)),
            transforms.ToTensor(),
            transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5)),
        ])
        transformedImages = preprocess(images).unsqueeze(0)
        return transformedImages

    def enhance(self, images):
        transformedImages = self._transform(images)
        with torch.no_grad():
            output = self.model(transformedImages)

        return output





