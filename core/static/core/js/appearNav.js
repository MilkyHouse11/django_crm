const mobileMenuBtn = document.getElementById('mobileMenuBtn');
const navList = document.getElementById('navList');

if (mobileMenuBtn && navList) {
    mobileMenuBtn.addEventListener('click', function () {
        navList.classList.toggle('show');
        mobileMenuBtn.classList.toggle('active');
    });
}