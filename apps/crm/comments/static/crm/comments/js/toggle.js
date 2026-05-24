function toggleComments(id, type) {
    const container = document.getElementById(`comments-container-${type}-${id}`)
    const icon = document.getElementById(`toggle-icon-${type}-${id}`)
    if (container.style.display === 'none') {
        container.style.display = 'block'
        icon.textContent = '▼'
        loadComments(id, type)
    } else {
        container.style.display = 'none'
        icon.textContent = '▶'
    }
}