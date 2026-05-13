// ==UserScript==
// @name         ExerciseDiary 汉化翻译
// @namespace    http://tampermonkey.net/
// @version      1.0
// @description  汉化ExerciseDiary锻炼日记工具网页界面
// @author       pixelpulse
// @match        http://192.168.31.210:9800/*
// @match        http://localhost:9800/*
// @grant        none
// @license MIT
// ==/UserScript==

(function () {
    'use strict';

    // 翻译映射表
    const translations = {
        // 导航栏
        'Add': '添加锻炼项目',
        'Stats': '锻炼统计',
        'Weight': '体重图表',
        'Config': '设置',

        // 首页
        'Exercise Diary': '锻炼日记',
        'Add weight': '添加体重',
        'Date': '日期',
        'Weight': '体重',
        'Save': '保存',
        'Name': '锻炼项名称',
        'Reps': '次数',
        'Add': '添加',
        'Add weight': '添加体重',

        // 添加页面
        'Exercise': '锻炼项',
        'Group': '所在项目组',
        'Place in group': '组内排序',
        'Description': '锻炼项描述',
        'Image link': '锻炼项图片URL链接',
        'Weight (default)': '项默认重量',
        'Reps (default)': '项默认次数',
        'Delete': '删除',
        'Image': '图片预览',

        // 统计页面
        'Reps': '次数',
        'Weight': '重量',
        'Exercise': '锻炼项目',
        'Date': '日期',
        'Reps': '次数',
        'Weight': '重量',
        'Chart': '图表',

        // 体重页面
        'Weight': '体重记录',
        'Date': '日期',
        'Weight': '体重',
        'Del': '删除',
        'Chart': '图表',
        'Add': '添加',

        // 设置页面
        'Config': '设置',
        'Host': '主机地址',
        'Port': '端口',
        'Theme': '主题',
        'Color mode': '颜色模式',
        'HeatMap Color': '热图颜色',
        'Page Step': '每页显示数量',
        'Auth': '认证',
        'Enable': '启用',
        'Expire after': '过期时间',
        'Login': '登录名',
        'New password': '新密码',
        'About': '关于',
        'light': '浅色',
        'dark': '深色',

        // 星期缩写
        'Mo': '周一',
        'Tu': '周二',
        'We': '周三',
        'Th': '周四',
        'Fr': '周五',
        'Sa': '周六',
        'Su': '周日',

        // 其他
        'Restart the app if changed': '更改后需要重启应用',
        'How many items to show on one page (for Weight and Stats)': '每页显示的项目数量（体重和统计页面）',
        'Authentication is only safe when used over HTTPS and with a strong password': '仅在使用HTTPS和强密码时认证才安全',
        'When user session expires. Can be set with suffixes m(minute), h(hour), d(day) or M(month). Default: 7d': '用户会话过期时间。可使用后缀m(分钟)、h(小时)、d(天)或M(月)。默认：7天',
        'Must not be empty': '不能为空',
        'Stored encrypted in config file': '以加密形式存储在配置文件中',
        'If you find this app useful, please, donate': '如果您觉得这个应用有用，请捐赠',
        'Commission you own app (Golang, HTML/JS). Contact and prices here': '定制您自己的应用（Golang, HTML/JS）。联系方式和价格请点击这里'
    };

    // 翻译函数
    function translateText(text) {
        if (!text || typeof text !== 'string') return text;

        // 去除首尾空格
        const trimmedText = text.trim();

        // 检查是否有翻译
        if (translations[trimmedText]) {
            return translations[trimmedText];
        }

        // 检查是否包含翻译
        for (const [key, value] of Object.entries(translations)) {
            if (text.includes(key)) {
                return text.replace(new RegExp(key, 'g'), value);
            }
        }

        return text;
    }

    // 翻译DOM节点
    function translateNode(node) {
        // 跳过script、style、textarea、input等元素
        if (node.nodeType === Node.ELEMENT_NODE) {
            const tagName = node.tagName.toLowerCase();
            if (['script', 'style', 'textarea', 'input', 'select', 'option'].includes(tagName)) {
                return;
            }

            // 翻译placeholder属性
            if (node.hasAttribute('placeholder')) {
                const placeholder = node.getAttribute('placeholder');
                const translated = translateText(placeholder);
                if (translated !== placeholder) {
                    node.setAttribute('placeholder', translated);
                }
            }

            // 翻译title属性
            if (node.hasAttribute('title')) {
                const title = node.getAttribute('title');
                const translated = translateText(title);
                if (translated !== title) {
                    node.setAttribute('title', translated);
                }
            }

            // 翻译aria-label属性
            if (node.hasAttribute('aria-label')) {
                const ariaLabel = node.getAttribute('aria-label');
                const translated = translateText(ariaLabel);
                if (translated !== ariaLabel) {
                    node.setAttribute('aria-label', translated);
                }
            }

            // 递归处理子节点
            node.childNodes.forEach(child => translateNode(child));
        }
        // 翻译文本节点
        else if (node.nodeType === Node.TEXT_NODE && node.textContent.trim()) {
            const originalText = node.textContent;
            const translatedText = translateText(originalText);

            if (translatedText !== originalText) {
                node.textContent = translatedText;
            }
        }
    }

    // 初始翻译
    function initialTranslation() {
        translateNode(document.body);

        // 翻译页面标题
        if (document.title) {
            const translatedTitle = translateText(document.title);
            if (translatedTitle !== document.title) {
                document.title = translatedTitle;
            }
        }
    }

    // 使用MutationObserver监听DOM变化
    function observeDOMChanges() {
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.type === 'childList') {
                    mutation.addedNodes.forEach((node) => {
                        if (node.nodeType === Node.ELEMENT_NODE) {
                            translateNode(node);
                        }
                    });
                }
            });
        });

        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    }

    // 等待页面加载完成后执行
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            initialTranslation();
            observeDOMChanges();
        });
    } else {
        initialTranslation();
        observeDOMChanges();
    }

    // 添加CSS样式
    const style = document.createElement('style');
    style.textContent = `
        /* 可以在这里添加一些自定义样式 */
        .tip-button {
            cursor: help;
        }
    `;
    document.head.appendChild(style);
})();