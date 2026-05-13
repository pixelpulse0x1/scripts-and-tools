链接：[動畫瘋评分显示增强](https://greasyfork.org/zh-CN/scripts/551950-動畫瘋评分显示增强)

# 动画疯评分显示增强脚本 (v3.0)

这是一个油猴（Userscript）脚本，专為台湾巴哈姆特动画疯 (`ani.gamer.com.tw`) 设计，旨在彻底革新您的动漫发现与浏览体验。

## 功能亮点

本脚本将“逐一点击查分”的繁琐模式，升级為“一键掌控所有资讯”的高效模式，并提供强大的交互功能。

- **🎬 按需加载**：在页面左下角提供一个控制面板，只有当您点击【获取评分】按钮时，脚本才会𫔭始工作，尊重您的浏览意图。
- **📊 数据排序与导出**：
- **即时排序**：点击【排序】按钮，可在弹窗中立即查看已获取动漫的评分降序排名。
- **导出表格**：在排序结果弹窗中，点击【导出為表格】可一键将排名、评分、名称、链接保存為 CSV 文件，方便您用 Excel 等工具进一步分析和收藏。
- **⭐ 自定义高亮**：在获取评分前，会弹窗询问您希望高亮显示的分数阈值（默认≥4.5分），让您一眼就能找到符合您标准的优质动漫。
- **⏯️ 高级控制**：在评分获取过程中，您可以随时**暂停**、**继续**或**停止**当前任务，完全掌控脚本的行為。暂停时仍可进行排序操作。
- **🎯 视觉锁定 (新)**：在排序结果中点击【定位】，对应的动漫卡片会出现**持久的蓝色锁定框**和酷炫的**动态声纳特效**，让您在茫茫片海中再也不会迷失目标。
- **🌐 通用支持**：完美支持动画疯的**首页**和**所有动画列表页** (`animeList.php`) 两种不同的页面佈局。
- **⚡ 双重缓存**：
- **性能缓存**：已获取过的评分会被自动缓存24小时，极大提升重複加载速度。
- **数据缓存**：用于排序的数据会保存在当前浏览会话中，即使暂停或停止，已获取的数据也不会丢失。
- **🛡️ 防屏蔽策略**：内置了随机延迟和偽装请求头等策略，模拟人类用户的浏览行為，有效避免触发网站的反爬虫机制。

## 安装步骤

1. **安装脚本管理器**：
您需要在浏览器中安装一个用户脚本管理器扩展。推荐使用 **Tampermonkey**。
* [Chrome / Edge 版本](https://chrome.google.com/webstore/detail/tampermonkey/dhdgffkkebhmkfjojejmpbldmpobfkfo)
* [Firefox 版本](https://addons.mozilla.org/firefox/addon/tampermonkey/)

2. **安装本脚本**：
* 点击浏览器右上角的 Tampermonkey 图标，选择“管理面板”。
* 在打𫔭的页面中，点击“+”号标签页来创建一个新脚本。
* 将本脚本的完整代码複製并粘贴到编辑器中，替换掉所有模板代码。
* 点击“文件” -> “保存”。

## 使用方法

1. 访问巴哈姆特动画疯网站。
2. 页面加载完成后，您会在左下角看到【排序】和【获取评分】按钮。
3. 点击【获取评分】，在弹窗中确认高亮阈值后，脚本将𫔭始工作，控制面板会变為【暂停】和【停止】。
4. 您可以随时点击【暂停】（此时【排序】按钮可用）或【停止】。
5. 在获取到数据后，点击【排序】按钮，即可在弹窗中查看结果。
6. 在弹窗中，您可以使用【定位】、【新窗口打𫔭】或【导出為表格】功能。

## 版本历史

- **V2.x**: 新增排序、导出為CSV、以及全新的“动态声纳”视觉锁定功能，并对UI和核心架构进行了最终优化。
- **V1.x **: 引入高级控制（暂停/继续/停止），重构為异步任务队列。
- **... (更早版本)**

---





# **油猴脚本【动画疯评分显示增强】技术交接文档**



项目版本: 2.2 (Final Annotated)

核心目标: 在ani.gamer.com.tw网站上，以模块化、高内聚低耦合的方式，提供评分获取、数据排序、结果导出和视觉定位等一系列增强功能，并赋予用户完全的过程控制能力。



#### **1. 核心架构设计**



本脚本的最终架构是围绕**“状态驱动的异步任务队列”**和**“持久化数据分层”**两个核心理念构建的。

- **状态驱动的异步任务队列 (State-Driven Asynchronous Task Queue)**：
- 此架构是為了实现【获取评分】过程中的**暂停/继续/停止**功能。
- **状态变量**: `isPaused`, `isStopped` 作為全局“𫔭关”，直接控制任务流。
- **任务队列**: `processingQueue` 数组作為待办事项列表。
- **链式调度**: 脚本摒弃了`forEach`批量调度模式。`processQueue`函数作為引擎，每次仅从队列取出一个任务交由`processAnimeCard`处理。`processAnimeCard`在异步网络请求结束后，才通过`setTimeout`调度下一次的`processQueue`调用。这个“处理完一个 -> 再调度下一个”的链条，使得我们可以在任意两个任务之间通过改变状态变量来中断或恢复流程。
- **持久化数据分层 (Persistent Data Layering)**：
- 脚本采用了两种不同的缓存机制，职责分离，互不干扰。
- **性能缓存 (`localStorage`)**: `CACHE_PREFIX`相关的缓存。其唯一目的是存储**单个动漫的评分**及其时间戳。当`processAnimeCard`遇到一个已处理过的动漫时，可以直接从这裡读取评分，避免重複的网络请求，极大提升性能。它的生命週期是24小时。
- **功能数据 (`sessionStorage`)**: `SORT_DATA_SESSION_KEY`相关的缓存。其唯一目的是存储**用于排序和导出的结构化数据**（名称、评分、链接等）。它在【获取评分】过程中被不断填充，并在【排序】和【导出】时被读取。它的生命週期是当前浏览会话，确保了即使用户暂停或停止，已获取的数据也不会丢失。



#### **2. 关键模块详解**



- **获取模块** (`promptAndFetch`, `startProcessing`, `processQueue`, `processAnimeCard`)
- 职责：响应用户的“获取”指令，构建任务队列，逐一请求数据，并将结果同时注入DOM（`injectRating`）、写入性能缓存（`saveToCache`）和功能数据缓存（`setSortData`）。
- **排序模块** (`handleSort`, `displaySortModal`)
- 职责：响应用户的“排序”指令，从`sessionStorage`中读取功能数据 (`getSortData`)，并将其与当前页面上的DOM元素重新关联。然后进行排序，并调用`displaySortModal`来生成弹窗界面。
- **导出模块** (`exportToCsv`)
- 职责：一个纯粹的工具函数。接收排序好的数据，将其格式化為带BOM头的UTF-8 CSV字符串，并通过创建临时`<a>`标签的方式触发浏览器下载。完全独立，高内聚。
- **视觉锁定模块** (`performVisualLock`, `clearCurrentHighlight`)
- 职责：提供醒目的视觉定位效果。`performVisualLock`负责添加蓝色边框类和注入“动态声纳”元素。`clearCurrentHighlight`则作為一个全局清理工具，被所有可能改变用户焦点的主按钮（获取、排序、暂停等）在执行前调用，以确保同一时间只有一个“锁定”目标。



#### **3. 数据流**



1. **用户点击【获取评分】**:
- `promptAndFetch` -> `startProcessing` (构建`processingQueue`，可选清除`sessionStorage`中的排序数据)。
- `processQueue` -> `processAnimeCard` (处理单个卡片)。
- `processAnimeCard` 内部分支:
- a. 读取 `localStorage` 性能缓存 -> `injectRating`。
- b. 网络请求 -> `saveToCache` (写入`localStorage`) -> `injectRating`。
- `injectRating` 内部:
- a. 注入评分到DOM。
- b. `setSortData` (添加/更新 `sessionStorage` 中的排序数据)。
- `processAnimeCard` 的回调 -> `setTimeout(processQueue)` (调度下一个任务)。
2. **用户点击【排序】**:
- `handleSort` -> `getSortData` (读取`sessionStorage`)。
- -> 重新关联DOM元素 -> `sort()` -> `displaySortModal`。
3. **用户点击【导出為表格】**:
- `displaySortModal`中的按钮 -> `exportToCsv` (接收排序数据，生成并下载CSV)。



#### **4. 未来维护与扩展指南**



- **网站佈局变更**:
- **卡片选择器**: 关注`startProcessing`函数中的`document.querySelectorAll(...)`。
- **动漫名称选择器**: 关注`injectRating`函数中的`card.querySelector(...)`链。
- **评分选择器**: 关注`processAnimeCard`函数中网络请求回调裡的`.score-overall-number`。
- **新增功能**:
- **UI相关**: 在`createControls`中添加元素，并在`resetUI`/`setProcessingUI`中管理其状态。
- **逻辑相关**: 遵循现有模块化思想。例如，要增加“按名称搜索”功能，可以在`handleSort`之后新增一个`handleSearch`函数，同样读取`getSortData`的数据，但执行`filter`操作而非`sort`。

该脚本目前架构清晰，各模块职责单一，应能轻鬆应对未来的需求变更。
