import React from 'react';
import { 
  Box, 
  Typography, 
  Container,
  Link,
  Divider
} from '@mui/material';
import { Email } from '@mui/icons-material';

function Feedback() {
  return (
    <Container maxWidth="md" sx={{ mt: 4, mb: 6 }}>
      <Box sx={{ textAlign: 'center', mb: 4 }}>
        <Typography 
          variant="h3" 
          component="h1"
          sx={{ 
            fontWeight: 'bold',
            mb: 3,
            color: 'primary.main'
          }}
        >
          Обратная связь
        </Typography>
        
        <Divider sx={{ my: 3 }} />
        
        <Typography 
          variant="h6"
          sx={{ 
            mb: 4,
            lineHeight: 1.6
          }}
        >
          Если у вас есть пожелания по работе приложения или вы обнаружили ошибки,
          вы можете сообщить об этом на почту:
        </Typography>
        
        <Box 
          sx={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: 2,
            mt: 4,
            mb: 6
          }}
        >
          <Email color="primary" fontSize="large" />
          <Link 
            href="mailto:cepsk3@gmail.com" 
            variant="h5"
            sx={{
              fontWeight: 'bold',
              color: 'primary.main',
              textDecoration: 'none',
              '&:hover': {
                textDecoration: 'underline'
              }
            }}
          >
            cepsk3@gmail.com
          </Link>
        </Box>
        
        <Typography 
          variant="body1"
          sx={{ 
            fontStyle: 'italic',
            color: 'text.secondary'
          }}
        >
          Мы ценим ваше мнение и постараемся ответить как можно скорее
        </Typography>
      </Box>
    </Container>
  );
}

export default Feedback;