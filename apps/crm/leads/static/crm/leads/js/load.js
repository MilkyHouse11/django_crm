async function load() {
    let search = document.querySelector('#search').value.trim()
    let source = document.querySelector('#filter-source').value
    let status = document.querySelector('#filter-status')?.value
    let grid = document.querySelector('.leads-grid')

    try {
        const response = await fetch(LOAD_LEADS_URL + `?page=${currentPage}&search=${search}&source=${source}&status=${status}`)
        const data = await response.json()

        let content = ''
        let leads = data['leads']
        let page = data['page']
        let pages = data['pages']
        let has_next = data['has_next']
        let has_previous = data['has_previous']

        document.querySelector('.current-page').textContent = page
        document.querySelector('.total-pages').textContent = pages

        let prevPage = document.querySelector('.prev-btn')
        let nextPage = document.querySelector('.next-btn')

        prevPage.onclick = () => {
            if (has_previous) {
                currentPage -= 1
                clicked = true
                load()
            }
        }
        nextPage.onclick = () => {
            if (has_next) {
                currentPage += 1
                clicked = true
                load()
            }
        }

        grid.innerHTML = ''

        prevPage.disabled = !has_previous
        nextPage.disabled = !has_next

        if (leads.length === 0) {
            grid.style.display = 'block'
            grid.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-text">No leads found</div>
                </div>
            `
            return
        }

        leads.forEach(lead_obj => {
            const dateString = lead_obj.created_at;
            const date = new Date(dateString);
            const formattedDate = date.toISOString().split('T')[0]

            let sourceOptions = []
            let statusOptions = []

            sources.forEach(source => {
                let selected = lead_obj.source == source ? 'selected' : ''
                sourceOptions.push(`<option value="${source}" ${selected}>${source}</option>`)
            })

            statuses.forEach(status => {
                let selected = lead_obj.status == status ? 'selected' : ''
                statusOptions.push(`<option value="${status}" ${selected}>${status}</option>`)
            })

            const sourceClass = lead_obj.source ? lead_obj.source.toLowerCase() : 'other'
            const statusClass = lead_obj.status ? lead_obj.status.toLowerCase() : 'new'

            let statusField = currentUserRole == 'manager' ? `<div>
                                <label>Status</label>
                                <label class="error" id="status-error-${lead_obj.id}"></label>
                                <select name="status">
                                    ${statusOptions.join('')}
                                </select>
                            </div>` : ''

            let postCommentButton = CAN_ADD_COMMENT ? `<form class="comment-form" onsubmit="submitComment(event, ${lead_obj.id}, 'lead')">
                                <input type="hidden" name="lead_id" value="${lead_obj.id}">
                                <div class="comment-form-group">
                                    <textarea name="content" class="comment-textarea" placeholder="Write a comment..." rows="2"></textarea>
                                </div>
                                <div class="comment-form-actions">
                                    <button type="submit" class="btn-submit-comment">Post Comment</button>
                                </div>
                            </form>` : ''

            let commentsSection = CAN_VIEW_COMMENT ? `<div class="comments-section" id="comments-${lead_obj.id}">
                        <button type="button" onclick="toggleComments('${lead_obj.id}', 'lead')" class="comments-header">
                            <a class="comments-title">Comments</a>
                            <span class="toggle-icon" id="toggle-icon-lead-${lead_obj.id}">▶</span>
                        </button>
                        <div class="comments-container" id="comments-container-lead-${lead_obj.id}" style="display: none;">
                            <div class="comments-list" id="comments-list-lead-${lead_obj.id}">
                                <div class="comments-loading">Loading comments...</div>
                            </div>
                            
                            ${postCommentButton}

                        </div>
                    </div>
                    ` : ''

            content += `
                <div class="lead-card" id="card-${lead_obj.id}">
                    <div class="card-header">
                        <div class="lead-name" id="name-${lead_obj.id}">${escapeHtml(lead_obj.full_name)}</div>
                        <div class="card-actions">
                            <button class="btn-edit-card" onclick="showEditForm(event)" id="${lead_obj.id}">Edit</button>
                        </div>
                    </div>
                    <div class="lead-contact">
                        <div class="lead-email">
                            <span id="email-${lead_obj.id}">${escapeHtml(lead_obj.email)}</span>
                        </div>
                        <div class="lead-phone">
                            <span id="phone-${lead_obj.id}">${escapeHtml(lead_obj.phone_number || '—')}</span>
                        </div>
                    </div>
                    <div class="lead-details">
                        <div class="detail-item">
                            Source: <span class="source-badge ${sourceClass}" id="source-${lead_obj.id}">${escapeHtml(lead_obj.source)}</span>
                        </div>
                        <div class="detail-item">
                            Status: <span class="status-badge ${statusClass}" id="status-${lead_obj.id}">${escapeHtml(lead_obj.status)}</span>
                        </div>
                        <div class="detail-item">
                            Active: <span class="active-badge ${lead_obj.is_active ? 'active' : 'inactive'}" id="status-${lead_obj.id}">${lead_obj.is_active ? 'Active' : 'Inactive'}</span>
                        </div>
                    </div>
                    <div class="assigned-to">
                        <span id="assigned-${lead_obj.id}">Assigned to: ${escapeHtml(lead_obj.assigned_to__email || '—')}</span>
                    </div>
                    
                    <div class="edit-card-form" id="edit-form-${lead_obj.id}" style="display: none;">
                        <form class="edit-form-card" onsubmit="confirmUpdate(event)" onreset="resetUpdate()" id="form-${lead_obj.id}">
                            ${CSRF_TOKEN}
                            
                            ${statusField}

                            <div>
                                <label>Full Name</label>
                                <label class="error" id="full_name-error-${lead_obj.id}"></label>
                                <input type="text" name="full_name" value="${escapeHtml(lead_obj.full_name)}" placeholder="Full name">
                            </div>
                            <div>
                                <label>Email</label>
                                <label class="error" id="email-error-${lead_obj.id}"></label>
                                <input type="email" name="email" value="${escapeHtml(lead_obj.email)}" placeholder="Email">
                            </div>
                            <div>
                                <label>Phone</label>
                                <label class="error" id="phone-error-${lead_obj.id}"></label>
                                <input type="text" name="phone" value="${escapeHtml(lead_obj.phone_number || '')}" placeholder="Phone">
                            </div>
                            <div>
                                <label>Source</label>
                                <label class="error" id="source-error-${lead_obj.id}"></label>
                                <select name="source">
                                    ${sourceOptions.join('')}
                                </select>
                            </div>

                            <div>
                                <label>Is Active</label>
                                <label class="error" id="is_active-error-${lead_obj.id}"></label>
                                <select name="is_active">
                                    ${lead_obj.is_active ? '<option value="true" selected>True</option><option value="false">False</option>' : '<option value="true">True</option><option value="false" selected>False</option>'}
                                </select>
                            </div>
                            <div class="edit-form-actions">
                                <button type="submit" class="btn-save">Save</button>
                                <button type="reset" class="btn-reset-card">Reset</button>
                                <button type="button" class="btn-cancel-card" onclick="hideEditForm(event, '${lead_obj.id}')">Cancel</button>
                            </div>
                        </form>
                    </div>

                    ${commentsSection}
                    
                </div>
            `
        })

        grid.innerHTML = content

        grid.style.display = 'grid'

        if (clicked) {
            window.scrollTo(0, document.body.scrollHeight)
            clicked = false
        }
    } catch (error) {
        grid.style.display = 'block'
        grid.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-text">Failed to load leads. Please try again.</div>
                </div>
            `
    }
}