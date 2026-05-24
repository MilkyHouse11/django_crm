async function load() {
    let search = document.querySelector('#search').value.trim()
    let stage = document.querySelector('#filter-stage').value
    let grid = document.querySelector('.deals-grid')

    try {
        const response = await fetch(LOAD_DEALS_URL + `?page=${currentPage}&search=${search}&stage=${stage}`)
        const data = await response.json()

        let content = ''
        let deals = data['deals']
        let page = data['page']
        let pages = data['pages']
        let has_next = data['has_next']
        let has_previous = data['has_previous']
        let leads = data['leads']

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

        if (deals.length === 0) {
            grid.style.display = 'block'
            grid.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-text">No deals found</div>
                </div>
            `
            return
        }

        deals.forEach(deal_obj => {
            const actualAmount = deal_obj.actual_amount ? `$${parseFloat(deal_obj.actual_amount).toFixed(2)}` : '—'
            const expectedAmount = `$${parseFloat(deal_obj.expected_amount).toFixed(2)}`
            const stageClass = deal_obj.stage.toLowerCase().replace(/_/g, '')
            const isClosed = !!deal_obj.closed_at

            let stageOptions = []

            stages.forEach(stage => {
                let selected = deal_obj.stage == stage ? 'selected' : ''
                stageOptions.push(`<option value="${stage}" ${selected}>${stage}</option>`)
            })

            const createCommentForm = ['won', 'lost'].includes(deal_obj.stage) ? '' :
             `<form class="comment-form" onsubmit="submitComment(event, ${deal_obj.id}, 'deal')">
                                <input type="hidden" name="deal_id" value="${deal_obj.id}">
                                <div class="comment-form-group">
                                    <textarea name="content" class="comment-textarea" placeholder="Write a comment..." rows="2"></textarea>
                                </div>
                                <div class="comment-form-actions">
                                    <button type="submit" class="btn-submit-comment">Post Comment</button>
                                </div>
                            </form>`

            content += `
                <div class="deal-card" id="card-${deal_obj.id}">
                    <div class="card-header">
                        <div class="deal-title" id="title-${deal_obj.id}">${escapeHtml(deal_obj.title)}</div>
                        <div class="card-actions">
                            ${!isClosed ? `<button class="btn-edit-card" onclick="showEditForm(event)" id="${deal_obj.id}">Edit</button>` : ''}
                        </div>
                    </div>
                    <div class="deal-lead" id="lead-${deal_obj.id}">${escapeHtml(deal_obj.lead_name)}</div>
                    <div class="deal-details">
                        <div class="detail-item">
                            <span class="amount-label">Expected:</span>
                            <span class="amount" id="expected-${deal_obj.id}">${expectedAmount}</span>
                        </div>
                        ${actualAmount !== '—' ? `
                            <div class="detail-item">
                                <span class="amount-label">Actual:</span>
                                <span id="actual-${deal_obj.id}">${actualAmount}</span>
                            </div>
                        ` : ''}
                        <div class="detail-item">
                            <span class="probability-label">Prob.:</span>
                            <span class="probability" id="probability-${deal_obj.id}">${deal_obj.probability}%</span>
                        </div>
                        <div class="detail-item">
                            <span class="stage-label">Stage:</span>
                            <span class="stage-badge ${stageClass}" id="stage-${deal_obj.id}">${deal_obj.stage}</span>
                        </div>
                    </div>
                    <div class="deal-dates">
                        <div class="date-item">
                            <span id="close-date-${deal_obj.id}">
                                Expected close: 
                                ${formatDateToUserTimezone(deal_obj.expected_close_date, format='date') || '—'}
                            </span>
                        </div>
                        ${deal_obj.closed_at ? `<div class="date-item">
                            <span>Closed:</span>
                            <span>${formatDateToUserTimezone(deal_obj.closed_at, format='date')}</span>
                        </div>` : ''}
                    </div>
                    
                    <div class="edit-card-form" id="edit-form-${deal_obj.id}" style="display: none;">
                        <form class="edit-form-card" onsubmit="confirmUpdate(event)" onreset="resetUpdate(event)" id="form-${deal_obj.id}">
                            ${CSRF_TOKEN}
                            <div>
                                <label class="error" id="__all__-error-${deal_obj.id}"></label>
                            </div>
                            <div>
                                <label>Lead</label>
                                <p>${deal_obj.lead_name}</p>
                            </div>
                            <div>
                                <label>Title</label>
                                <label class="error" id="title-error-${deal_obj.id}"></label>
                                <input type="text" name="title" value="${escapeHtml(deal_obj.title)}" placeholder="Title">
                            </div>
                            <div>
                                <label>Expected Amount</label>
                                <label class="error" id="expected_amount-error-${deal_obj.id}"></label>
                                <input type="number" name="expected_amount" value="${deal_obj.expected_amount}" step="0.01" placeholder="Expected amount">
                            </div>
                            <div class="actual-amount-field" id="actual-amount-${deal_obj.id}" style="display: none;">
                                <label>Actual Amount</label>
                                <label class="error" id="actual_amount-error-${deal_obj.id}"></label>
                                <input type="number" name="actual_amount" value="${deal_obj.actual_amount || ''}" step="0.01" placeholder="Actual amount">
                            </div>
                            <div class="stage-select" id="select-${deal_obj.id}">
                                <label>Stage</label>
                                <label class="error" id="stage-error-${deal_obj.id}"></label>
                                <select name="stage" id="stage-select-${deal_obj.id}">
                                    ${stageOptions.join('')}
                                </select>
                            </div>
                            <div>
                                <label>Probability</label>
                                <label class="error" id="probability-error-${deal_obj.id}"></label>
                                <input type="number" name="probability" value="${deal_obj.probability}" min="0" max="100" placeholder="Probability">
                            </div>
                            <div>
                                <label>Expected Close Date</label>
                                <label class="error" id="expected_close_date-error-${deal_obj.id}"></label>
                                <input type="date" name="expected_close_date" value="${deal_obj.expected_close_date || ''}">
                            </div>
                            <div class="edit-form-actions">
                                <button type="submit" class="btn-save">Save</button>
                                <button type="reset" class="btn-reset-card">Reset</button>
                                <button type="button" class="btn-cancel-card" onclick="hideEditForm(event, '${deal_obj.id}')">Cancel</button>
                            </div>
                        </form>
                    </div>

                    <div class="comments-section" id="comments-${deal_obj.id}">
                        <button type="button" onclick="toggleComments(${deal_obj.id}, 'deal')" class="comments-header">
                            <a class="comments-title">Comments</a>
                            <span class="toggle-icon" id="toggle-icon-deal-${deal_obj.id}">▶</span>
                        </button>
                        <div class="comments-container" id="comments-container-deal-${deal_obj.id}" style="display: none;">
                            <div class="comments-list" id="comments-list-deal-${deal_obj.id}">
                                <div class="comments-loading">Loading comments...</div>
                            </div>
                            ${createCommentForm}
                        </div>
                    </div>

                </div>
            `
        })

        grid.innerHTML = content
        
        grid.style.display = 'grid'
        
        loadEditForms()

        if (clicked) {
            window.scrollTo(0, document.body.scrollHeight)
            clicked = false
        }
    } catch (error) {
        grid.style.display = 'block'
            grid.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-text">Failed to load deals. Please try again.</div>
                </div>
            `
    }
}

function loadEditForms() {
    let stageSelects = document.querySelectorAll('.stage-select')
    let closedStages = ['won', 'lost']

    stageSelects.forEach(stageSelect => {
        let selectId = stageSelect.id.split('-')
        selectId = selectId[selectId.length - 1]

        let actualAmountField= document.querySelector(`#actual-amount-${selectId}`)
        let role = stageSelect.value
        
        if (closedStages.includes(role)) {
            actualAmountField.style.display = role == 'won' ? 'block' : 'none'
        }

        stageSelect.addEventListener('change', (event) => {
            let role = event.target.value
            if (closedStages.includes(role)) {
                actualAmountField.style.display = role == 'won' ? 'block' : 'none'
            }
            else {
                actualAmountField.style.display = 'none'
                actualAmountInput.value = ''
            }
        })
    })
}