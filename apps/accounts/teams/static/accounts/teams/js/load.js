async function load() {
    let search = document.querySelector('#search').value.trim()
    let company = document.querySelector('#filter-company')?.value || 'all'
    let grid = document.querySelector('.teams-grid')

    try {
        const response = await fetch(LOAD_TEAMS_URL + `?page=${currentPage}&search=${search}&company=${company}`)
        const data = await response.json()

        let content = ''
        let teams = data['teams']
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

        if (teams.length === 0) {
            grid.style.display = 'block'
            grid.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-text">No teams found</div>
                </div>
            `
            return
        }

        teams.forEach(team_obj => {
            const formattedDate = formatDateToUserTimezone(team_obj.created_at, format = 'date')

            content += `
    <div class="team-card" id="card-${team_obj.id}">
        <div class="card-header">
            <div class="team-name" id="name-${team_obj.id}">${escapeHtml(team_obj.name)}</div>
            <div class="card-actions">
                <button class="btn-edit-card" onclick="showEditForm(event)" id="${team_obj.id}">Edit</button>
            </div>
        </div>
        <div class="team-company" id="company-name-${team_obj.id}">${escapeHtml(team_obj.company_name)}</div>
        <div class="team-stats">
            <div class="stat-item">
                <span>${team_obj.members_count || 0} members</span>
            </div>
        </div>
        <div class="team-details">
            <div class="detail-item">
                Status: <span class="status-badge ${team_obj.is_active ? 'active' : 'inactive'}" id="status-${team_obj.id}">${team_obj.is_active ? 'Active' : 'Inactive'}</span>
            </div>
        </div>
        <div class="team-meta">
            <span>Created: ${formattedDate || '—'}</span>
        </div>
        <div class="edit-card-form" id="edit-form-${team_obj.id}" style="display: none;">
            <form class="edit-form-card" onsubmit="confirmUpdate(event)" onreset="resetUpdate()" id="form-${team_obj.id}">
                ${CSRF_TOKEN}
                <div>
                    <label>Team Name</label>
                    <label class="error" id="name-error-${team_obj.id}"></label>
                    <input type="text" name="name" value="${escapeHtml(team_obj.name)}" placeholder="Team name">
                </div>
                <div>
                    <label>Is Active</label>
                    <label class="error" id="is_active-error-${team_obj.id}"></label>
                    <select name="is_active">
                        ${team_obj.is_active ? '<option value="true" selected>True</option><option value="false">False</option>' : '<option value="true">True</option><option value="false" selected>False</option>'}
                    </select>
                </div>
                <div class="edit-form-actions">
                    <button type="submit" class="btn-save">Save</button>
                    <button type="reset" class="btn-reset-card">Reset</button>
                    <button type="button" class="btn-cancel-card" onclick="hideEditForm(event, '${team_obj.id}')">Cancel</button>
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
                    <div class="empty-state-text">Failed to load teams. Please try again.</div>
                </div>
            `
    }
}