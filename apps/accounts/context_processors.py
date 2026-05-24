def user_permissions(request):
    user_permissions = request.user.get_all_permissions()
    context = {'user_permissions': user_permissions}
    objects = ['lead', 'deal', 'comment', 'user', 'team', 'company']
    actions = ['add', 'view', 'change', 'delete']

    for object in objects:
        for action in actions:
            context[f'can_{action}_{object}'] = bool([p for p in user_permissions if f'{action}_{object}' in p])

    return context

def user_role(request):
    if request.user.is_authenticated:
        role = ' '.join(request.user.role.name.capitalize().split('_'))
        return {'user_role': role}
    return {'user_role': ''}