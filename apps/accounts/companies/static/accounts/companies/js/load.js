async function load() {
    let search = document.querySelector('#search').value.trim()
    let grid = document.querySelector('.companies-grid')

    try {
        const response = await fetch(LOAD_COMPANIES_URL + `?page=${currentPage}&search=${search}`)
        const data = await response.json()

        let content = ''
        let companies = data['companies']
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

        if (companies.length === 0) {
            grid.style.display = 'block'
            grid.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-text">No companies found</div>
                </div>
            `
            return
        }

        companies.forEach(company_obj => {
            const formattedDate = formatDateToUserTimezone(company_obj.created_at, fromat = 'date')

            content += `
                <div class="company-card" id="card-${company_obj.id}">
                    <div class="card-header">
                        <div class="company-name" id="name-${company_obj.id}">${escapeHtml(company_obj.name)}</div>
                        <div class="card-actions">
                            <button class="btn-edit-card" onclick="showEditForm(event, '${company_obj.id}')" id="${company_obj.id}">Edit</button>
                        </div>
                    </div>
                    <div class="company-details">
                        <div class="detail-item">
                            Status: <span class="status-badge ${company_obj.is_active ? 'active' : 'inactive'}" id="status-${company_obj.id}">${company_obj.is_active ? 'Active' : 'Inactive'}</span>
                        </div>
                    </div>
                    <div class="company-meta">
                        <span>Created: ${formattedDate || '—'}</span>
                    </div>
                    <div class="edit-card-form" id="edit-form-${company_obj.id}" style="display: none;">
                        <form class="edit-form-card" onsubmit="confirmUpdate(event)" id="form-${company_obj.id}">
                            ${CSRF_TOKEN}
                            <div>
                                <label>Company Name</label>
                                <label class="error" id="name-error-${company_obj.id}"></label>
                                <input type="text" name="name" value="${escapeHtml(company_obj.name)}" placeholder="Company name">
                            </div>
                            <div>
                                <label>Is Active</label>
                                <label class="error" id="is_active-error-${company_obj.id}"></label>
                                <select name="is_active">
                                    ${company_obj.is_active ? '<option value="true" selected>True</option><option value="false">False</option>' : '<option value="true">True</option><option value="false" selected>False</option>'}
                                </select>
                            </div>
                            <div class="edit-form-actions">
                                <button type="submit" class="btn-save">Save</button>
                                <button type="button" class="btn-cancel-card" onclick="hideEditForm(event, '${company_obj.id}')">Cancel</button>
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
        grid.style.display = 'block'
        grid.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-text">Failed to load companies. Please try again.</div>
                </div>
            `
    }
}

document.addEventListener('DOMContentLoaded', function () {
    load();
});