# bricks

# :link: Git 規則 #

1. 分支簡介：
    
    - master：正式發布版本

    - development：開發階段，合併版本測試

    - <頁面名>：該頁面功能的版本測試

    - <功能>：該功能的版本測試（影響到整個系統的功能故須獨立出分支）
2. 分支建立：
    
    `git branch 分支名`

3. PR(Pull Request) 步驟：
   
    1. 切換到想要 push 的分支： `git checkout 分支名`
   
    2. 將檔案加入： `git add .`

    3. 設定版本名稱： `git commit -m "版本名稱"`

    4. push 上去分支： `git push origin 分支名`

4. Merge 分支步驟：

    1. 點選頁首 pull requests

    假如可以 auto merge(出現綠色字時)，直接按 merge commit
    
    假如有版本衝突，不能 auto merge(出現灰色字時)：
    
        1. 點選 PR conversation 中 merge conflict 方框的右上角檢視衝突的地方
  
        2. 手動進行修改，並按右上角的儲存

        3. 回到 PR conversation 頁面，點選 merge commit 即可

參考資料
    
[理解如何在Github使用Pull Request (PR)](https://hackmd.io/@judyyutong/understandPR#4-%E7%99%BC%E9%80%81-Pull-Request-%E8%AB%8B%E6%B1%82%E5%90%88%E4%BD%B5)
    
[猴子都能懂得Git入門指南-進階篇](https://backlog.com/git-tutorial/tw/stepup/stepup1_4.html)

[Git Flow 是什麼？為什麼需要這種東西？](https://gitbook.tw/chapters/gitflow/why-need-git-flow)
       
# :link: Install Instruction #

1. Install [Git](https://git-scm.com/)

    - https://backlog.com/git-tutorial/tw/

    - https://miahsuwork.medium.com/%E7%AC%AC%E4%BA%8C%E9%80%B1-git-%E6%9C%AC%E5%9C%B0%E7%AB%AF%E8%88%87%E9%81%A0%E7%AB%AF%E6%93%8D%E4%BD%9C-github-78eec4537179

2. Download [Tomcat](https://tomcat.apache.org/)

3.開啟cmd(命令提示字元)輸入以下指令碼

`cd (your folder path)`

`git init`

`git remote add 本地端名稱 https://github.com/WAFFLE900/bricks.git`

*`origin` 通常被預設成本地端名稱，可以改成自己喜歡的名稱

GitHub共用教學網站：

[GitHub共用教學網站](https://saffranblog.coderbridge.io/2020/12/01/github-collaboration/)

[GitHub共用教學網站1](https://medium.com/tsungs-blog/day13-git-github%E6%93%8D%E4%BD%9C-304ad94a1c6a)

[GitHub共用教學網站2](https://www.freecodecamp.org/chinese/news/git-rename-branch-how-to-change-a-local-branch-name/)

[上傳下載整合教學](https://gitbook.tw/chapters/github/fail-to-push)

[上傳下載整合教學2](https://www.796t.com/content/1549601292.html)

[GitHub上傳指令1](https://w3c.hexschool.com/git/b9be5b1e)

[GitHub上傳指令2](https://ithelp.ithome.com.tw/articles/10266697)

[GitHub本地端帳號登入](https://blog.csdn.net/weixin_43215322/article/details/109405983)

# :file_folder: Upload Files #

open your cmd(命令提示字元)

`cd (your folder path)`

`git add .` *加入所在資料夾內所有檔案
或 `git add 檔案名稱` *加入該檔案或資料夾

`git commit -m 版本名稱` *建立新版本

`git pull --rebase 本地端名稱 master` *將檔案及資料夾從遠端拉下來本地端整合

`git push -u origin master` *將整合好的檔案及資料夾上傳到遠端

# :file_folder: Download Files #

In your computer's folder, use the command below :

`cd (your folder path)`

`git pull 本地端名稱 master`

then you can refresh the data weekly to download file from GitHub.

### If it has a conflict during the download HW

You can try

`cd (your folder path)`

`git add .`

`git commit -m "write some message"`

`git merge master`

then pull again.

# 🌐 後端網站 #

https://docs.netlify.com/configure-builds/file-based-configuration/

*Pythonanywhere*

網址:

https://www.pythonanywhere.com/

教學:

https://ithelp.ithome.com.tw/articles/10308084?sc=rss.qu


# 📓 Django學習資源 #

Template語法：

https://ithelp.ithome.com.tw/articles/10212469

# 🤥 雜七雜八 #
網址：

https://app.netlify.com/sites/profound-strudel-3890fa/overview

教學：

[用 Netlify 佈署前端網頁 (一)](https://ithelp.ithome.com.tw/articles/10256925)

[用 Netlify 佈署前端網頁 (二)](https://ithelp.ithome.com.tw/articles/10257115)

[用 Netlify Functions 佈署 Line Bot](https://ithelp.ithome.com.tw/articles/10257235)

[探索 Netlify Functions 的暫存空間](https://ithelp.ithome.com.tw/articles/10257364?sc=rss.qu)

[用 Netlify 整合前後端服務](https://ithelp.ithome.com.tw/articles/10257884?sc=pt)

npm安裝使用教學:

https://ithelp.ithome.com.tw/articles/10234060

nodejs安裝:
https://nodejs.org/en/download/

netlify cli安裝雜七雜八:

https://www.youtube.com/watch?v=n_KASTN0gUE

https://blog.csdn.net/DMLong_x/article/details/111191599

dijango vs. netlify

https://www.netlify.com/blog/2016/04/08/a-step-by-step-guide-cactus-on-netlify/#netlifystart

https://www.reddit.com/r/django/comments/colbdd/is_it_possible_to_host_a_django_app_in_netlify/

https://answers.netlify.com/t/support-guide-can-i-run-a-web-server-http-listener-and-or-database-at-netlify/3078

超簡易教學:

https://bojne.medium.com/%E4%B8%89%E6%AD%A5%E9%A9%9F%E7%94%A8-netlify-%E8%BC%95%E9%AC%86%E6%9E%B6%E7%B6%B2%E7%AB%99-67d65ce135f6

netlify簡介

https://blog.alantsai.net/posts/2018/07/migrate-blog-to-ssg-demo-devops-8-netlify-free-static-site-hosting-service

前端佈署

https://www.youtube.com/watch?v=oiV7jz_56cA

其他資源+雜七雜八

https://jimmyswebnote.com/static-web-pages-vs-dynamic-web-pages/

https://techmoon.xyz/000webhost/


