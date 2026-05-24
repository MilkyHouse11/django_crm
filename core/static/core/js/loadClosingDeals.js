async function loadClosingDeals() {
    try {
        const now = new Date();
        const weekFromNow = new Date(now.getTime() + 7 * 24 * 60 * 60 * 1000);
        const weekFromNowLocal = weekFromNow.toLocaleDateString('en');
        const nowLocal = now.toLocaleDateString('en');
        const response = await fetch(LOAD_DEALS_URL + `?page=${currentPage}&datel=${weekFromNowLocal}&dateg=${nowLocal}`)
        const data = await response.json()

        let grid = document.querySelector('.deals-grid')
        let content = ''
        let deals = data['deals']
        let page = data['page']
        let pages = data['pages']
        let has_next = data['has_next']
        let has_previous = data['has_previous']
        let leads = data['leads']
        let stages = data['stages']

        document.querySelector('.current-page').textContent = page
        document.querySelector('.total-pages').textContent = pages

        let prevPage = document.querySelector('.prev-btn')
        let nextPage = document.querySelector('.next-btn')

        prevPage.onclick = () => {
            if (has_previous) {
                currentPage -= 1
                clicked = true
                loadDeals()
            }
        }
        nextPage.onclick = () => {
            if (has_next) {
                currentPage += 1
                clicked = true
                loadDeals()
            }
        }

        grid.innerHTML = ''

        prevPage.disabled = !has_previous
        nextPage.disabled = !has_next

        if (deals.length === 0) {
            grid.style.display = 'block'
            grid.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-text">No closing deals found</div>
                </div>
            `
            return
        }

        deals.forEach(deal_obj => {
            const actualAmount = deal_obj.actual_amount ? `$${parseFloat(deal_obj.actual_amount).toFixed(2)}` : '—'
            const expectedAmount = `$${parseFloat(deal_obj.expected_amount).toFixed(2)}`
            const stageClass = deal_obj.stage.toLowerCase().replace(/_/g, '')
            const isClosed = !!deal_obj.closed_at

            let leadOptions = []
            let stageOptions = []

            leads.forEach(lead => {
                let selected = deal_obj.lead_id == lead.id ? 'selected' : ''
                leadOptions.push(`<option value="${lead.id}" ${selected}>${escapeHtml(lead.full_name)}</option>`)
            })

            stages.forEach(stage => {
                let selected = deal_obj.stage == stage ? 'selected' : ''
                stageOptions.push(`<option value="${stage}" ${selected}>${stage}</option>`)
            })

            content += `
                <div class="deal-card" id="card-${deal_obj.id}">
                    <div class="card-header">
                        <span class="deal-id">#${deal_obj.id}</span>
                        <div class="card-actions">
                            <form action="${DEAL_DELETE_URL.replace('1', deal_obj.id)}" method="post" style="display: inline;">
                                ${CSRF_TOKEN}
                                <button type="submit" class="btn-delete-card">Delete</button>
                            </form>
                            ${!isClosed ? `<button class="btn-edit-card" onclick="showEditForm(event)" id="${deal_obj.id}">Edit</button>` : ''}
                        </div>
                    </div>
                    <div class="deal-title" id="title-${deal_obj.id}">${escapeHtml(deal_obj.title)}</div>
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
                            <span id="close-date-${deal_obj.id}">Expected close: ${deal_obj.expected_close_date || '—'}</span>
                        </div>
                        ${deal_obj.closed_at ? `<div class="date-item"><span>Closed:</span><span>${deal_obj.closed_at}</span></div>` : ''}
                    </div>
                    <div class="edit-card-form" id="edit-form-${deal_obj.id}" style="display: none;">
                        <form class="edit-form-card" onsubmit="confirmUpdate(event, 'deal')" onreset="resetUpdate(event)" id="form-${deal_obj.id}">
                            ${CSRF_TOKEN}
                            <div>
                                <label>Lead</label>
                                <label class="error" id="lead-error-${deal_obj.id}"></label>
                                <select name="lead">
                                    ${leadOptions.join('')}
                                </select>
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
                            <div class="closed-at-field" id="closed-at-${deal_obj.id}" style="display: none;">
                                <label>Closed At</label>
                                <label class="error" id="closed_at-error-${deal_obj.id}"></label>
                                <input type="date" name="closed_at" value="${deal_obj.closed_at || ''}" placeholder="Closed at">
                            </div>
                            <div class="edit-form-actions">
                                <button type="submit" class="btn-save">Save</button>
                                <button type="reset" class="btn-reset-card">Reset</button>
                                <button type="button" class="btn-cancel-card" onclick="hideEditForm(event, '${deal_obj.id}')">Cancel</button>
                            </div>
                        </form>
                    </div>
                </div>
            `
        })

        grid.style.display = 'grid'
        grid.innerHTML = content

        if (clicked) {
            window.scrollTo(0, document.body.scrollHeight)
            clicked = false
        }
    } catch (error) {
        console.error('Error loading deals:', error)
        let grid = document.querySelector('.deals-grid')
        if (grid) {
            grid.style.display = 'block'
            grid.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-text">Failed to load deals. Please try again.</div>
                </div>
            `
        }
    }
}