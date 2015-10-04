
void execute(py::object &self) {
  py::object param_name("ksize");
  py::tuple parameters(1);
  parameters.set_item(0, param_name);
  int ksize = (int)self.mcall("get_param", parameters);

  printf("sup %d\n", ksize);
}
