def hitby_user(self,request):
    hitby_id = request.user
    full_name = request.user.fullname or ""  
    full_name = f"{full_name}".strip().upper()
    if full_name:
        bkp_hitby_name =full_name
    else:
        bkp_hitby_name = request.user.email    
    return hitby_id, bkp_hitby_name if bkp_hitby_name else None
 
 
