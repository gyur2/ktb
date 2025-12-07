// =============================
// SPA ROUTER 기본 설정
// =============================
const app = document.getElementById("app");

// 라우트 테이블 정의
const routes = {
  "": renderHome,
  "#home": renderHome,
  "#login": renderLogin,
  "#signup": renderSignup,
  "#board": renderBoard,
  "#post": renderPostDetail,       // #post?id=1
  "#post-write": renderPostWrite,
  "#post-edit": renderPostEdit,    // #post-edit?id=1
  "#profile-edit": renderProfileEdit,
  "#password-edit": renderPasswordEdit,
};

// 현재 해시 기준으로 화면 렌더링
function renderCurrentPage() {
  // [수정] 페이지 변경 시 기존 스크롤 이벤트 제거
  window.onscroll = null;

  const hash = window.location.hash.split("?")[0];
  const renderer = routes[hash] || renderHome;
  renderer();
}

// 해시 변경 감지
window.addEventListener("hashchange", renderCurrentPage);

// 첫 로딩 시 렌더링
document.addEventListener("DOMContentLoaded", () => {
  if (!window.location.hash) {
    window.location.hash = "#home";
  }
  renderCurrentPage();
});

// 화면 전환 함수
function navigate(path) {
  window.location.hash = path;
}

// =============================
// 공통 API 래퍼
// =============================
const API_BASE = "http://localhost:8000"; // FastAPI 주소

async function apiRequest(url, method = "GET", body = null, isFile = false) {
  const headers = {};

  // 파일 업로드가 아니면 JSON 헤더
  if (!isFile) {
    headers["Content-Type"] = "application/json";
  }

  // ✅ 여기서 토큰을 읽어서 Authorization 헤더 추가
  const token = localStorage.getItem("access_token");
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  try {
    const res = await fetch(API_BASE + url, {
      method,
      headers,
      body: isFile ? body : body ? JSON.stringify(body) : null,
    });

    let data = {};
    try {
      data = await res.json();
    } catch (_) {
      // body 없는 응답일 수 있음
    }

    if (!res.ok) {
      const msg =
        (data && (data.message || data.detail)) ||
        "요청 처리 중 오류가 발생했습니다.";
      alert(msg);
      throw new Error(msg);
    }

    return data;
  } catch (err) {
    console.error("API ERROR:", err);
    throw err;
  }
}


// =============================
// 로그인 상태 관리
// =============================
function saveUser(user) {
  localStorage.setItem("user", JSON.stringify(user));
}

function getUser() {
  const raw = localStorage.getItem("user");
  if (!raw) return null;
  try {
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

function requireLogin() {
  const user = getUser();
  if (!user) {
    alert("로그인이 필요합니다.");
    navigate("#login");
    return false;
  }
  return true;
}

function logout() {
  localStorage.removeItem("user");
  localStorage.removeItem("access_token");
  alert("로그아웃 되었습니다.");
  navigate("#login");
}


// =============================
// 유틸 함수
// =============================

// 쿼리 파라미터 추출 (#post?id=1 같은 형태에서)
function getQueryParams() {
  const hash = window.location.hash;
  const [, queryString] = hash.split("?");
  if (!queryString) return {};
  return Object.fromEntries(new URLSearchParams(queryString));
}

// HTML 이스케이프
function escapeHtml(str = "") {
  return str.replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

// 비밀번호 규칙 검사
function validatePasswordRule(pw) {
  // 8~20자, 대/소문자/숫자/특수문자 1개 이상
  const lengthOk = pw.length >= 8 && pw.length <= 20;
  const upper = /[A-Z]/.test(pw);
  const lower = /[a-z]/.test(pw);
  const digit = /[0-9]/.test(pw);
  const special = /[^A-Za-z0-9]/.test(pw);
  return lengthOk && upper && lower && digit && special;
}

// 이메일 형식 검사(간단 버전)
function isValidEmail(email) {
  if (email.length < 5) return false;
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return re.test(email);
}

// 닉네임 검사
function validateNickname(nick) {
  if (!nick) return { ok: false, msg: "닉네임을 입력해주세요." };
  if (/\s/.test(nick)) {
    return { ok: false, msg: "닉네임에는 공백을 사용할 수 없습니다." };
  }
  if (nick.length > 10) {
    return { ok: false, msg: "닉네임은 최대 10자까지 작성 가능합니다." };
  }
  return { ok: true, msg: "" };
}

// 이미지 미리보기
function previewImage(file, imgElement) {
  const reader = new FileReader();
  reader.onload = () => {
    imgElement.src = reader.result;
  };
  reader.readAsDataURL(file);
}

// 공통 헤더(상단 바) HTML
function renderHeader() {
  const user = getUser();
  const hash = window.location.hash.split("?")[0];

  // 어떤 화면인지에 따라 토글 상태 결정
  const boardHashes = ["#board", "#post", "#post-write", "#post-edit"];
  const isBoardPage = boardHashes.includes(hash);

  const toggleLabel = isBoardPage ? "홈 🏠" : "게시판 📫";
  const toggleTarget = isBoardPage ? "#home" : "#board";
  const toggleModeClass = isBoardPage ? "toggle-light" : "toggle-dark";
  let avatarHtml = "";
  if (user && user.profile_image) {
    const imgUrl = `${API_BASE}/${user.profile_image}`;
    avatarHtml = `<img src="${imgUrl}" class="profile-avatar-img" alt="프로필" />`;
  } else {
    avatarHtml = `<div class="profile-avatar-fallback">🙂</div>`;
  }
  return `
    <header class="top-bar">
      <div class="top-left">
        <div class="top-title" onclick="navigate('#home')">🍊과즙상 커뮤니티</div>
        <button 
          class="toggle-nav-btn ${toggleModeClass}" 
          id="toggleHomeBoard"
          data-target="${toggleTarget}"
        >
          ${toggleLabel}
        </button>
      </div>
      <div class="top-right">
        ${
          user
            ? `
          <div class="profile-chip" id="profileMenuToggle">
            ${avatarHtml}
            <span class="profile-name">${escapeHtml(user.nickname || "사용자")}</span>
          </div>
          <div class="profile-menu" id="profileMenu" style="display:none;">
            <button class="menu-item" id="goProfileEdit">회원정보 수정</button>
            <button class="menu-item" id="goPasswordEdit">비밀번호 수정</button>
            <button class="menu-item" id="btnLogout">로그아웃</button>
          </div>
        `
            : `
          <button class="secondary-btn" id="goLogin">로그인</button>
        `
        }
      </div>
    </header>
  `;
}

// 헤더 이벤트 바인딩
function bindHeaderEvents() {
  const goLogin = document.getElementById("goLogin");
  if (goLogin) {
    goLogin.addEventListener("click", () => navigate("#login"));
  }
  const profileMenuToggle = document.getElementById("profileMenuToggle");
  const profileMenu = document.getElementById("profileMenu");
  if (profileMenuToggle && profileMenu) {
    profileMenuToggle.addEventListener("click", () => {
      profileMenu.style.display =
        profileMenu.style.display === "none" ? "block" : "none";
    });

    document.body.addEventListener("click", (e) => {
      if (
        !profileMenu.contains(e.target) &&
        !profileMenuToggle.contains(e.target)
      ) {
        profileMenu.style.display = "none";
      }
    });
  }

  const goProfileEdit = document.getElementById("goProfileEdit");
  if (goProfileEdit) {
    goProfileEdit.addEventListener("click", () => {
      navigate("#profile-edit");
    });
  }

  const goPasswordEdit = document.getElementById("goPasswordEdit");
  if (goPasswordEdit) {
    goPasswordEdit.addEventListener("click", () => {
      navigate("#password-edit");
    });
  }

  const btnLogout = document.getElementById("btnLogout");
  if (btnLogout) {
    btnLogout.addEventListener("click", () => logout());
  }
  const toggleBtn = document.getElementById("toggleHomeBoard");
  if (toggleBtn) {
    toggleBtn.addEventListener("click", () => {
      const target = toggleBtn.dataset.target || "#board";
      navigate(target);
    });
  }
}