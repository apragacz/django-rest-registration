export default function getFormFieldChangeHandler(element, name) {
  return (event) => {
    const { value } = event.target;
    element.setState((prevState) => {
      const formData = { ...prevState.formData };
      formData[name] = value;
      return { formData };
    });
  };
}
