from scipy.weave import ext_tools
from ..filter import Filter
from ..filter_descriptor import FilterDescriptor
from ..parameter_descriptor import ParameterDescriptor
from ..io_descriptor import IODescriptor
from ...IO.image import Image
import cv2
import os
import inspect

class TestCPPFilter(Filter):
    descriptor = FilterDescriptor("TestCPP", "Blurs an image using the normalized box filter.",
                                  inputs=[IODescriptor("input", "Source image.", Image)],
                                  outputs=[IODescriptor("output", "Blured image.", Image)],
                                  parameters=[ParameterDescriptor("ksize", "Blurring kernel size.", int, 3, 1, 1024)])

    def initialize(self):
        print "Init %s" % self.name

        code_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "filter.cpp")
        code = open(code_path).read()

        modname = 'TestCPPFilterCompiled'
        mod = ext_tools.ext_module(modname)

        mod.customize.add_header("<Python.h>")
        mod.customize.add_extra_link_arg("`pkg-config --cflags --libs opencv python`")
        mod.customize.add_extra_link_arg("-L/usr/local/cuda/lib64")

        descriptor = TestCPPFilter.descriptor
        func = ext_tools.ext_function('_execute', 'execute(self);', ['self'])
        func.customize.add_support_code(code)
        mod.add_function(func)

        mod.compile()

        self.mod = __import__(modname)

    def execute(self, time=0):
        im = self.get_input("input")

        if im:
            self.mod._execute(self)

            ksize = self.get_param("ksize")
            im2 = Image(cv2.blur(im.get_image(), (ksize, ksize)))
            im.copy_header(im2)
            self.set_output("output", im2)
