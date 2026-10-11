import React from 'react';
import { Route, Routes } from 'react-router-dom';
import LeaveBalance from './LeaveBalance';
import LeaveApplication from './LeaveApplication';

const ELMRoutes = () => {
  return (
    <Routes>
      <Route path="balance" element={<LeaveBalance />} />
      <Route path="application" element={<LeaveApplication />} />
    </Routes>
  );
};

export default ELMRoutes;
