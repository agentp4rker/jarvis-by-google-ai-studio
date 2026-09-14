/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import { Terminal, Download, Code2, Smartphone, Monitor } from 'lucide-react';

export default function App() {
  return (
    <div className="min-h-screen bg-neutral-950 text-cyan-400 font-mono p-8 flex flex-col items-center justify-center">
      <div className="max-w-4xl w-full space-y-8">
        <div className="text-center space-y-4">
          <h1 className="text-4xl md:text-6xl font-bold tracking-tighter text-cyan-300">J.A.R.V.I.S.</h1>
          <p className="text-cyan-600 text-lg">System Integration Protocol Active</p>
        </div>
        
        <div className="bg-neutral-900 border border-cyan-900/50 rounded-xl p-8 shadow-2xl shadow-cyan-900/20">
          <div className="flex items-center gap-3 mb-6 border-b border-cyan-900/50 pb-4">
            <Terminal className="w-6 h-6" />
            <h2 className="text-xl font-semibold text-cyan-100">Implementation Ready</h2>
          </div>
          
          <p className="text-neutral-400 mb-6 leading-relaxed">
            Pełna, produkcyjna implementacja systemu J.A.R.V.I.S. w języku Python została wygenerowana zgodnie ze specyfikacją. 
            Pliki źródłowe (Windows PC + Android WebSocket) znajdują się w katalogu <code className="bg-neutral-950 px-2 py-1 rounded text-cyan-300 border border-neutral-800">/jarvis</code>.
          </p>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="bg-neutral-950 p-4 rounded-lg border border-neutral-800 flex items-start gap-4 hover:border-cyan-800 transition-colors">
              <Monitor className="w-8 h-8 text-cyan-500 shrink-0" />
              <div>
                <h3 className="font-semibold text-cyan-200">Desktop Control</h3>
                <p className="text-sm text-neutral-500 mt-1">pywin32, psutil, pyqt6 HUD overlay.</p>
              </div>
            </div>
            <div className="bg-neutral-950 p-4 rounded-lg border border-neutral-800 flex items-start gap-4 hover:border-cyan-800 transition-colors">
              <Smartphone className="w-8 h-8 text-cyan-500 shrink-0" />
              <div>
                <h3 className="font-semibold text-cyan-200">Phone Controller</h3>
                <p className="text-sm text-neutral-500 mt-1">WebSocket server, SMS & Calls automation.</p>
              </div>
            </div>
            <div className="bg-neutral-950 p-4 rounded-lg border border-neutral-800 flex items-start gap-4 hover:border-cyan-800 transition-colors">
              <Code2 className="w-8 h-8 text-cyan-500 shrink-0" />
              <div>
                <h3 className="font-semibold text-cyan-200">Gemini Bridge</h3>
                <p className="text-sm text-neutral-500 mt-1">Function Calling & Tool Dispatcher.</p>
              </div>
            </div>
            <div className="bg-neutral-950 p-4 rounded-lg border border-neutral-800 flex items-start gap-4 hover:border-cyan-800 transition-colors">
              <Terminal className="w-8 h-8 text-cyan-500 shrink-0" />
              <div>
                <h3 className="font-semibold text-cyan-200">Autonomous Agents</h3>
                <p className="text-sm text-neutral-500 mt-1">Incoming/Outgoing call handlers.</p>
              </div>
            </div>
          </div>
          
          <div className="mt-8 p-4 bg-cyan-950/20 border border-cyan-900/50 rounded-lg">
            <p className="text-sm text-cyan-400/80">
              Aby użyć systemu J.A.R.V.I.S., wykorzystaj panel plików środowiska, aby pobrać katalog <strong>/jarvis</strong> i uruchomić go natywnie w środowisku Windows 11 (wymagany Python 3.11+).
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
