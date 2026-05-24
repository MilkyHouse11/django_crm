async function loadComments(id, type) {
    const commentsList = document.getElementById(`comments-list-${type}-${id}`)
    try {
        const url = COMMENTS_URL.replace("1", id).replace('type', type)
        const response = await fetch(url)
        const data = await response.json()
        
        if (data.comments && data.comments.length > 0) {
            commentsList.innerHTML = data.comments.map(comment => `
                <div class="comment-item" id="comment-${comment.id}">
                    <div class="comment-header">
                        <strong class="comment-author">${escapeHtml(comment.author_email || 'User')}</strong>
                        <span class="comment-date">
                            ${formatDateToUserTimezone(comment.created_at)}
                        </span>
                    </div>
                    <div class="comment-content">${escapeHtml(comment.content)}</div>
                </div>
            `).join('')
        } else {
            commentsList.innerHTML = '<div class="comments-empty">No comments yet.</div>'
        }
    } catch (error) {
        commentsList.innerHTML = '<div class="comments-error">Failed to load comments</div>'
    }
}