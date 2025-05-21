import React from 'react';
import { Tooltip, IconButton, Box, Typography } from '@mui/material';
import InfoIcon from '@mui/icons-material/Info';

const getCurrentWeekType = () => {
  const referenceDates = [
    { date: new Date('2023-04-28'), type: 'Ч' },
    { date: new Date('2023-05-05'), type: 'Н' },
  ].sort((a, b) => b.date - a.date);

  const now = new Date();
  const closestReference = referenceDates.find(ref => ref.date <= now);
  
  if (closestReference) {
    const weeksPassed = Math.floor((now - closestReference.date) / (7 * 24 * 60 * 60 * 1000));
    return weeksPassed % 2 === 0 ? closestReference.type : closestReference.type === 'Ч' ? 'Н' : 'Ч';
  }
  
  return 'Ч';
};

const WeekIndicator = () => {
  const currentWeekType = getCurrentWeekType();
  const weekName = currentWeekType === 'Ч' ? 'Чётная' : 'Нечётная';

  return (
    <Tooltip title={`Сейчас ${weekName.toLowerCase()} неделя`} arrow>
      <IconButton 
        size="small" 
        sx={{ 
          position: 'fixed', 
          top: 80, 
          right: 16,
          backgroundColor: 'background.paper',
          '&:hover': {
            backgroundColor: 'action.hover'
          }
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <InfoIcon color="primary" />
          <Typography variant="body2" sx={{ ml: 1 }}>
            {weekName}
          </Typography>
        </Box>
      </IconButton>
    </Tooltip>
  );
};

export default WeekIndicator;