"use client";

import * as React from "react";
import {
  Wrench,
  Bot,
  MessageCircle,
  Brain,
  Activity,
  Sparkles,
} from "lucide-react";

import { NavMain } from "./nav-main";
import { NavUser } from "./nav-user";
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarRail,
} from "@/components/ui/sidebar";
import { SiteHeader } from "./sidebar-header";
import { useI18n } from "@/i18n/provider";

export function AppSidebar({ ...props }: React.ComponentProps<typeof Sidebar>) {
  const { dictionary } = useI18n();
  const data = {
    navMain: [
      {
        title: dictionary.nav.chat,
        url: "/",
        icon: MessageCircle,
      },
      {
        title: dictionary.nav.agents,
        url: "/agents",
        icon: Bot,
      },
      {
        title: dictionary.nav.tools,
        url: "/tools",
        icon: Wrench,
      },
      // {
      //   title: "Inbox",
      //   url: "/inbox",
      //   icon: Inbox,
      // },
      {
        title: dictionary.nav.rag,
        url: "/rag",
        icon: Brain,
      },
      {
        title: dictionary.nav.runs,
        url: "/runs",
        icon: Activity,
      },
      {
        title: dictionary.nav.jarvis,
        url: "/jarvis",
        icon: Sparkles,
      },
    ],
  };
  return (
    <Sidebar
      collapsible="icon"
      {...props}
    >
      <SiteHeader />
      <SidebarContent>
        <NavMain items={data.navMain} />
      </SidebarContent>
      <SidebarFooter>
        <NavUser />
      </SidebarFooter>
      <SidebarRail />
    </Sidebar>
  );
}
