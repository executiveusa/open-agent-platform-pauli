"use client";

import { SidebarProvider, SidebarInset } from "@/components/ui/sidebar";
import { AppSidebar } from "./app-sidebar";
import { AgentsProvider } from "@/providers/Agents";
import { MCPProvider } from "@/providers/MCP";
import { RagProvider } from "@/features/rag/providers/RAG";
import { I18nProvider } from "@/i18n/provider";

export function SidebarLayout({ children }: { children: React.ReactNode }) {
  return (
    <SidebarProvider>
      <MCPProvider>
        <AgentsProvider>
          <RagProvider>
            <I18nProvider>
              <AppSidebar />
              <SidebarInset>{children}</SidebarInset>
            </I18nProvider>
          </RagProvider>
        </AgentsProvider>
      </MCPProvider>
    </SidebarProvider>
  );
}
