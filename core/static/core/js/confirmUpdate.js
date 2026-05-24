async function confirmUpdate(e) {
    e.preventDefault();

    const currentForm = e.target;
    const formData = new FormData(currentForm);
    const formId = currentForm.id.replace('form-', '');
    const url = UPDATE_URL.replace('1', formId);

    try {
        const response = await fetch(url, {
            method: 'POST',
            body: formData
        });

        const result = await response.text();

        if (!result.includes('DOCTYPE')) {
            const errors = JSON.parse(result);
            Object.keys(errors).forEach(field => {
                const errorLabel = document.getElementById(`${field}-error-${formId}`);
                if (errorLabel) {
                    errorLabel.textContent = errors[field];
                }
            });
        } else {
            location.reload();
        }
    } catch (error) {
        console.error('Ошибка при обновлении:', error);
    }
}