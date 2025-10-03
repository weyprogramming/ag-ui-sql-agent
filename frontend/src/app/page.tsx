"use client";

import Chat from "./components/Chat";
import DashboardState from "./components/DashboardConfig";

export default function CopilotKitPage() {

  return (
    <main>
      <MainContent/>
    </main>
  );
}

const MainContent = () => {
  return(<div className="flex">
    <div className="flex-1">
      <DashboardState/>
      <Chat/>
    </div>
  </div> 
  )
}