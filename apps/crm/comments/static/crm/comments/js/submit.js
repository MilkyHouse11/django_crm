async function submitComment(event, id, type) {
    event.preventDefault()

    const temp = document.createElement('div');
    temp.innerHTML = CSRF_TOKEN;
    const token = temp.firstElementChild.value;

    const form = event.target
    const textarea = form.querySelector('textarea[name="content"]')
    const content = textarea.value.trim()

    if (!content) {
        alert('Please enter a comment')
        return
    }

    const formData = new FormData()
    formData.append('content', content)
    formData.append(type, id)

    try {
        const response = await fetch(ADD_COMMENT, {
            method: 'POST',
            headers: {
                'X-CSRFToken': token
            },
            body: formData
        })

        if (response.ok) {
            textarea.value = ''
            loadComments(id, type)
        } else {
            const error = await response.json()
            alert(error.message || 'Failed to post comment')
        }
    } catch (error) {
        console.error('Error posting comment:', error)
        alert('Failed to post comment. Please try again.')
    }
}