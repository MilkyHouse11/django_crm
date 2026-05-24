function showEditForm(event) {
    const id = event.currentTarget.id;
    const form = document.getElementById(`edit-form-${id}`);
    const formDisplay = form.style.display

    if (formDisplay == 'block') {
        hideEditForm(event, id)
        return
    }
    form.style.display = 'block';
}

function hideEditForm(event, id) {
    document.getElementById(`edit-form-${id}`).style.display = 'none';
}