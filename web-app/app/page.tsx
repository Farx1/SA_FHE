'use client';

import { useState } from 'react';
import Hero from '@/components/Hero';
import ProjectGoal from '@/components/ProjectGoal';
import ProjectOverview from '@/components/ProjectOverview';
import Architecture from '@/components/Architecture';
import FHEProcess from '@/components/FHEProcess';
import DatasetInfo from '@/components/DatasetInfo';
import Features from '@/components/Features';
import DemoSection from '@/components/DemoSection';
import Footer from '@/components/Footer';

export default function Home() {
  return (
    <main className="min-h-screen bg-black">
      <Hero />
      <ProjectGoal />
      <ProjectOverview />
      <DatasetInfo />
      <Architecture />
      <FHEProcess />
      <Features />
      <DemoSection />
      <Footer />
      </main>
  );
}
