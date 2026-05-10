---
title: "Sephoration"
---

<div class="home-welcome">
  <p class="welcome-text">欢迎来到我的个人博客，这里记录着我关于技术、学习和生活的思考。</p>
</div>

<div class="home-highlights">
  <div class="highlight-card">
    <div class="highlight-icon"><i class="fa-solid fa-microchip"></i></div>
    <h3>操作系统</h3>
    <p>计算机核心知识笔记，从进程管理到内存管理，系统化学习记录。</p>
  </div>
  <div class="highlight-card">
    <div class="highlight-icon"><i class="fa-solid fa-code"></i></div>
    <h3>技术探索</h3>
    <p>编程实践与技术思考，在代码的世界里不断探索前行。</p>
  </div>
  <div class="highlight-card">
    <div class="highlight-icon"><i class="fa-solid fa-lightbulb"></i></div>
    <h3>思考随笔</h3>
    <p>关于协同、价值与成长的思考，记录每一个灵感的瞬间。</p>
  </div>
</div>

<style>
.home-welcome {
  text-align: center;
  padding: 2rem 1rem 1rem;
}
.home-welcome .welcome-text {
  font-size: 1.1rem;
  color: var(--fi-global-font-secondary-color);
  max-width: 600px;
  margin: 0 auto;
  line-height: 1.8;
}
.home-highlights {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
  padding: 1rem 0 2rem;
}
.home-highlights .highlight-card {
  text-align: center;
  padding: 1.5rem;
  border-radius: 12px;
  border: 1px solid var(--fi-global-border-color);
  transition: all 0.3s ease;
  background: var(--fi-global-background-color);
}
.home-highlights .highlight-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0,0,0,0.1);
  border-color: transparent;
}
[data-theme=dark] .home-highlights .highlight-card:hover {
  box-shadow: 0 8px 24px rgba(0,0,0,0.4);
}
.home-highlights .highlight-icon {
  font-size: 2rem;
  margin-bottom: 0.75rem;
}
.home-highlights .highlight-card:nth-child(1) .highlight-icon { color: #667eea; }
.home-highlights .highlight-card:nth-child(2) .highlight-icon { color: #764ba2; }
.home-highlights .highlight-card:nth-child(3) .highlight-icon { color: #f093fb; }
.home-highlights h3 {
  font-size: 1.1rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
}
.home-highlights p {
  font-size: 0.9rem;
  color: var(--fi-global-font-secondary-color);
  line-height: 1.6;
}
</style>
