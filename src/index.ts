import express, { Request, Response } from "express";
import cors from "cors";
import fetch from "node-fetch";

const app = express();
const PORT = process.env.PORT || 3000;

app.get("/health", (req: Request, res: Response) => {
  res.json({ code: 1, msg: "running", date: "running" });
});

app.get("/api/fetch", (req: Request, res: Response) => {
  try {
    const targetUrl = req.query.url as string;
    if (!targetUrl) {
      res.json({ code: 400, msg: "缺少参数 url" });
      return;
    }

    if (!targetUrl.includes("qgiga.com")) {
      res.json({ code: 403, msg: "不允许抓取该域名" });
      return;
    }

    fetch(targetUrl, {
      timeout: 25000,
      headers: {
        "User-Agent":
          "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile Safari/604.1",
        "Accept-Language": "zh-CN,zh;q=0.9",
      },
      redirect: "follow",
    })
      .then((resp) => {
        resp
          .text()
          .then((text) => {
            res.json({
              code: 1,
              msg: "成功",
              date: text,
            });
          })
          .catch((err) => {
            res.json({
              code: 0,
              msg: "失败",
              date: err.message,
            });
          });
      })
      .catch((err) => {
        res.json({
          code: 0,
          msg: "失败",
          date: err.message,
        });
      });
  } catch (err: any) {
    res.status(500).json({
      code: 500,
      msg: "页面请求失败",
      data: err.message,
    });
  }
});


app.listen(PORT, () => {
    console.log(`服务启动 on port ${PORT}`);
})
