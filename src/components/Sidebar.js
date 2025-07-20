import React from 'react';
import { 
  Cloud, 
  Grid, 
  Image, 
  Music, 
  Type, 
  MessageSquare, 
  FileText, 
  Star, 
  FolderOpen 
} from 'lucide-react';

const sidebarItems = [
  { id: 'media', label: 'Media', icon: Cloud },
  { id: 'stock', label: 'Stock videos', icon: Grid },
  { id: 'photos', label: 'Photos', icon: Image },
  { id: 'audio', label: 'Audio', icon: Music },
  { id: 'text', label: 'Text', icon: Type },
  { id: 'captions', label: 'Captions', icon: MessageSquare },
  { id: 'transcript', label: 'Transcript', icon: FileText },
  { id: 'stickers', label: 'Stickers', icon: Star },
];

const Sidebar = ({ activeTab, onTabChange }) => {
  return (
    <div className="w-16 bg-dark-900 border-r border-dark-700 flex flex-col items-center py-4">
      {/* Logo placeholder */}
      <div className="mb-8">
        <div className="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center text-white font-bold text-sm">
          LOGO
        </div>
      </div>

      {/* Navigation items */}
      <div className="flex-1 flex flex-col gap-2">
        {sidebarItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          
          return (
            <button
              key={item.id}
              onClick={() => onTabChange(item.id)}
              className={`sidebar-item ${isActive ? 'active' : ''}`}
              title={item.label}
            >
              <Icon className="w-5 h-5" />
            </button>
          );
        })}
      </div>

      {/* Bottom item */}
      <div className="mt-auto">
        <button className="sidebar-item" title="Files">
          <FolderOpen className="w-5 h-5" />
        </button>
      </div>
    </div>
  );
};

export default Sidebar; 