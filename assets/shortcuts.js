document.addEventListener('keydown', function (event) {
  if (event.ctrlKey && event.key === 'Enter') {
    const button = document.getElementById('run-simulation');
    if (button) button.click();
  }
});
