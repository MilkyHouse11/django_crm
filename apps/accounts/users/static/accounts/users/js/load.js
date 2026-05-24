async function load() {
    try {
        let email = document.querySelector('#search').value.trim()
        let role = document.querySelector('#filter-role')?.value
        let company = document.querySelector('#filter-company')
        let grid = document.querySelector('.users-grid')

        if (company) {
            company = company.value
        }

        let response = await fetch(LOAD_USERS_URL + `?page=${currentPage}&email=${email}&role=${role}&company=${company}`)
        let data = await response.json()

        let content = ''
        let users = data['users']
        let page = data['page']
        let pages = data['pages']
        let has_next = data['has_next']
        let has_previous = data['has_previous']
        let teams = data['teams']

        document.querySelector('.current-page').textContent = page
        document.querySelector('.total-pages').textContent = pages

        let prevPage = document.querySelector('.prev-btn')
        let nextPage = document.querySelector('.next-btn')

        prevPage.onclick = () => {
            if (has_previous) {
                if (currentPage <= 1) return
                currentPage -= 1
                clicked = true
                load()
            }
        }
        nextPage.onclick = () => {
            if (has_next) {
                if (currentPage == pages) return
                currentPage += 1
                clicked = true
                load()
            }
        }

        grid.innerHTML = ''

        prevPage.disabled = !has_previous
        nextPage.disabled = !has_next

        if (users.length === 0) {
            grid.style.display = 'block'
            grid.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-text">No users found</div>
                </div>
            `
            return
        }

        users.forEach(user_obj => {
            let roleOptions = []
            let teamOptions = []
            let companyOptions = []

            roles.forEach(role => {
                let selected = user_obj.role_name == role.name ? 'selected' : ''
                roleOptions.push(`<option value="${role.id}" ${selected}>${role.name}</option>`)
            })

            companies.forEach(company => {
                let selected = user_obj.company_id == company.id ? 'selected' : ''
                companyOptions.push(`<option value="${company.id}" ${selected}>${company.name}</option>`)
            })

            teams.forEach(team => {
                let isUserTeam = user_obj.team_id == team.id
                let selected = isUserTeam ? 'selected' : ''
                if (isUserTeam || team.members_count < 50) {
                    teamOptions.push(`<option value="${team.id}" ${selected}>${team.company_name + ': ' + team.name}</option>`)
                }
            })

            let companyField = USER_PERMISSIONS.includes('users.global_change_user') ? `<div>
                                <label>Company</label>
                                <label class="error" id="team-error-${user_obj.id}"></label>
                                <select name="company">
                                    <option value="">None</option>
                                    ${companyOptions.join('')}
                                </select>
                            </div>` : ''

            let teamField = USER_PERMISSIONS.includes('users.company_change_user') ? `<div>
                                <label>Team</label>
                                <label class="error" id="team-error-${user_obj.id}"></label>
                                <select name="team">
                                    <option value="">None</option>
                                    ${teamOptions.join('')}
                                </select>
                            </div>` : ''

            const initials = (user_obj.first_name?.[0] || 'U') + (user_obj.last_name?.[0] || '')
            const fullName = `${user_obj.first_name || ''} ${user_obj.last_name || ''}`.trim() || 'No name'

            content += `
                <div class="user-card" id="card-${user_obj.id}">
                    <div class="card-header">
                        <div class="user-name" id="name-${user_obj.id}">${escapeHtml(fullName)}</div>
                        <div class="card-actions">
                            <button class="btn-edit-card" onclick="showEditForm(event)" id="${user_obj.id}">Edit</button>
                        </div>
                    </div>
                    <div class="user-avatar">
                        <div class="user-info">
                            <div class="user-email" id="email-${user_obj.id}">${escapeHtml(user_obj.email)}</div>
                        </div>
                    </div>
                    <div class="user-details">
                        <div class="detail-item">
                            Role: <span class="role-badge" id="role-${user_obj.id}">${escapeHtml(user_obj.role_name)}</span>
                        </div>
                        <div class="detail-item">
                            Team: <span class="team-badge" id="team-${user_obj.id}">${escapeHtml(user_obj.team_name) || '—'}</span>
                        </div>
                        <div class="detail-item">
                            Company: <span class="company-badge" id="company-${user_obj.id}">${escapeHtml(user_obj.company_name) || '—'}</span>
                        </div>
                        <div class="detail-item">
                            Status: <span class="status-badge ${user_obj.is_active ? 'active' : 'inactive'}" id="status-${user_obj.id}">${user_obj.is_active ? 'Active' : 'Inactive'}</span>
                        </div>
                    </div>
                    <div class="edit-card-form" id="edit-form-${user_obj.id}" style="display: none;">
                        <form class="edit-form-card" onsubmit="confirmUpdate(event)" onreset="resetUpdate()" id="form-${user_obj.id}">
                            ${CSRF_TOKEN}
                            <div>
                                <label class="error" id="__all__-error-${user_obj.id}"></label>
                            </div>
                            <div>
                                <label>First Name</label>
                                <label class="error" id="first_name-error-${user_obj.id}"></label>
                                <input type="text" name="first_name" value="${escapeHtml(user_obj.first_name)}" placeholder="First name">
                            </div>
                            <div>
                                <label>Last Name</label>
                                <label class="error" id="last_name-error-${user_obj.id}"></label>
                                <input type="text" name="last_name" value="${escapeHtml(user_obj.last_name)}" placeholder="Last name">
                            </div>
                            <div>
                                <label>Email</label>
                                <label class="error" id="email-error-${user_obj.id}"></label>
                                <input type="email" name="email" value="${escapeHtml(user_obj.email)}" placeholder="Email">
                            </div>
                            <div>
                                <label>Password</label>
                                <label class="error" id="password-error-${user_obj.id}"></label>
                                <input type="password" name="password" placeholder="New password (leave blank to keep current)">
                            </div>
                            <div>
                                <label>Role</label>
                                <label class="error" id="role-error-${user_obj.id}"></label>
                                <select name="role">
                                    ${roleOptions.join('')}
                                </select>
                            </div>
                            
                            ${companyField}
                            
                            ${teamField}

                            <div>
                                <label>Is Active</label>
                                <label class="error" id="is_active-error-${user_obj.id}"></label>
                                <select name="is_active">
                                    ${user_obj.is_active ? '<option value="true" selected>True</option><option value="false">False</option>' : '<option value="true">True</option><option value="false" selected>False</option>'}
                                </select>
                            </div>
                            <div class="edit-form-actions">
                                <button type="submit" class="btn-save">Save</button>
                                <button type="reset" class="btn-reset-card">Reset</button>
                                <button type="button" class="btn-cancel-card" onclick="hideEditForm(event, '${user_obj.id}')">Cancel</button>
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
                    <div class="empty-state-text">Failed to load users. Please try again.</div>
                </div>
            `
    }
}