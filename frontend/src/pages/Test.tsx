import { useRef, useEffect, useState } from "react";

const Main = () => {
  const socket = useRef<WebSocket>();
  const chzzk_id = "6e06f5e1907f17eff543abd06cb62891";
  const chat_id = "N1bTIh";
  const chatChannelAccessToken =
    "Ux6YeIUWDOu3nIbK+nK7mJ9gks8PVGrlkvRyT0/pT/s0miC6bRUPYG+zLO/Dru34";

  const [sid, setSid] = useState<string | null>(null);
  const [uuid, setUuid] = useState<string | null>(null);

  useEffect(() => {
    socket.current = new WebSocket("wss://kr-ss2.chat.naver.com/chat");
    socket.current.onopen = () => {
      socket.current?.send(
        JSON.stringify({
          ver: "3",
          cmd: 100,
          svcid: "game",
          cid: chat_id,
          bdy: {
            uid: null,
            devType: 2001,
            accTkn: chatChannelAccessToken,
            auth: "READ",
            libVer: "4.9.3",
            osVer: "Android/6.0",
            devName: "Google Chrome/131.0.0.0",
            locale: "ko",
            timezone: "Asia/Seoul",
          },
          tid: 1,
        })
      );
    };

    socket.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      console.log(data.cmd, typeof data.cmd);

      switch (data.cmd) {
        case 10100:
          console.log("10100", data);
          setSid(data.bdy.sid);
          setUuid(data.bdy.uuid);
          console.log("sid", data.bdy.sid);
          console.log("uuid", data.bdy.uuid);
          break;
        case 0:
          socket.current?.send(
            JSON.stringify({
              ver: "2",
              cmd: 10000,
            })
          );
          break;
      }
    };

    socket.current.onerror = (error) => {
      console.log("error", error);
    };

    socket.current.onclose = () => {
      console.log("close");
    };

    return () => {
      if (socket.current && socket.current.readyState === 1) {
        socket.current.close();
      }
    };
  }, []);

  return <></>;
};

export default Main;
